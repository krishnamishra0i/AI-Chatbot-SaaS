"""
Chat routes — /api/chat, /api/chat/stream, and /v1/chat/completions
Real-time streaming pipeline with memory support.
"""

import time
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.core.config import get_settings
from api.schemas.schemas import ChatRequest, ChatResponse, ChatCompletionRequest
from api.services import chat_service
from api.services.usage_service import record_usage
from api.services.memory_service import get_memory
from api.services.prompt_engine import get_system_prompt
from api.dependencies import get_optional_user

settings = get_settings()
router = APIRouter(tags=["Chat"])
memory = get_memory()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, db: AsyncSession = Depends(get_db), user=Depends(get_optional_user)):
    """Chat endpoint with memory and streaming support."""
    session_id = body.session_id or "default"

    # Build context window with memory
    context_messages = memory.get_context_window(
        session_id=session_id,
        system_prompt="",  # system prompt handled inside chat_service
        user_message=body.message,
    )
    # Remove empty system message from memory context
    context_messages = [m for m in context_messages if m.get("content")]

    if body.stream:
        async def event_stream():
            full_content = ""
            async for chunk in chat_service.chat_completion_stream(
                context_messages,
                model=body.model,
                temperature=body.temperature,
                max_tokens=body.max_tokens,
            ):
                full_content += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            # Store in memory
            memory.add_turn(session_id, "user", body.message)
            memory.add_turn(session_id, "assistant", full_content)
            yield f"data: {json.dumps({'type': 'done', 'content': full_content})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    result = await chat_service.chat_completion(
        messages=context_messages,
        model=body.model,
        temperature=body.temperature,
        max_tokens=body.max_tokens,
    )

    # Store in memory
    memory.add_turn(session_id, "user", body.message)
    memory.add_turn(session_id, "assistant", result["content"])

    # Track usage if authenticated
    if user:
        await record_usage(
            db=db,
            user_id=user.id,
            service="chat",
            tokens=result.get("tokens", 0),
        )

    return ChatResponse(
        message=result["content"],
        session_id=session_id,
        tokens_used=result.get("tokens", 0),
        latency_ms=result.get("latency_ms", 0),
        model=result.get("model", "unknown"),
        provider=result.get("provider", "unknown"),
        timestamp=datetime.now(timezone.utc),
    )


@router.post("/api/chat/stream")
async def chat_stream(body: ChatRequest):
    """
    Dedicated streaming endpoint (SSE).
    Optimised for real-time TTS pipeline — yields sentence chunks.
    """
    session_id = body.session_id or "default"
    context_messages = memory.get_context_window(
        session_id=session_id,
        system_prompt="",
        user_message=body.message,
    )
    context_messages = [m for m in context_messages if m.get("content")]

    async def event_stream():
        full_content = ""
        sentence_buffer = ""
        async for chunk in chat_service.chat_completion_stream(
            context_messages,
            model=body.model,
            temperature=body.temperature,
            max_tokens=body.max_tokens,
        ):
            full_content += chunk
            sentence_buffer += chunk

            # Emit sentence-level chunks for TTS pipeline
            for sep in [". ", "! ", "? ", ".\n", "!\n", "?\n"]:
                while sep in sentence_buffer:
                    idx = sentence_buffer.find(sep)
                    sentence = sentence_buffer[:idx + 1].strip()
                    sentence_buffer = sentence_buffer[idx + len(sep):]
                    if sentence:
                        yield f"data: {json.dumps({'type': 'sentence', 'content': sentence})}\n\n"

            # Also send raw tokens for display
            yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

        # Flush remaining
        if sentence_buffer.strip():
            yield f"data: {json.dumps({'type': 'sentence', 'content': sentence_buffer.strip()})}\n\n"

        memory.add_turn(session_id, "user", body.message)
        memory.add_turn(session_id, "assistant", full_content)
        yield f"data: {json.dumps({'type': 'done', 'content': full_content})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/api/memory/{session_id}")
async def get_memory_info(session_id: str):
    """Get conversation memory for a session."""
    return {
        "info": memory.get_session_info(session_id),
        "messages": memory.get_messages(session_id),
    }


@router.delete("/api/memory/{session_id}")
async def clear_memory(session_id: str):
    """Clear conversation memory for a session."""
    memory.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}


@router.get("/api/memory")
async def list_memory_sessions():
    """List all active memory sessions."""
    return {"sessions": memory.list_sessions()}


@router.post("/v1/chat/completions")
async def chat_completions(body: ChatCompletionRequest):
    """
    OpenAI-compatible /v1/chat/completions endpoint.
    Supports streaming via SSE.
    """
    if body.stream:
        async def event_stream():
            async for chunk in chat_service.chat_completion_stream(
                messages=body.messages,
                model=body.model,
                temperature=body.temperature,
                max_tokens=body.max_tokens,
            ):
                data = {
                    "id": "chatcmpl-athena",
                    "object": "chat.completion.chunk",
                    "model": body.model,
                    "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}],
                }
                yield f"data: {json.dumps(data)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    result = await chat_service.chat_completion(
        messages=body.messages,
        model=body.model,
        temperature=body.temperature,
        max_tokens=body.max_tokens,
    )

    return {
        "id": "chatcmpl-athena",
        "object": "chat.completion",
        "model": result.get("model", body.model),
        "provider": result.get("provider", "unknown"),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": result["content"]},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": result.get("tokens", 0),
            "total_tokens": result.get("tokens", 0),
        },
    }
