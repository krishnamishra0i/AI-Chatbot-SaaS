"""
Chat routes — /api/chat, /api/chat/stream, and /v1/chat/completions
Real-time streaming pipeline with memory support + subscription limits.
"""

import time
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header
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
from api.services.subscription_manager import subscription_manager
from api.services.optimization_config import get_chat_limit
from api.middleware.jwt_auth import get_optional_user_from_jwt
from api.services.chat_storage_service import chat_storage

settings = get_settings()
router = APIRouter(tags=["Chat"])
memory = get_memory()


def estimate_tokens(text: str) -> int:
    """Estimate tokens in text (rough: 1 token per 4 chars)."""
    return max(1, len(text) // 4)


@router.post("/api/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    jwt_user=Depends(get_optional_user_from_jwt),
):
    """Chat endpoint with subscription limits enforced and JWT authentication."""
    # Determine user ID from JWT or use session_id as fallback
    final_user_id = jwt_user['user_id'] if jwt_user else body.session_id or "default"
    session_id = body.session_id or final_user_id
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 1: CHECK SUBSCRIPTION LIMITS
    # ════════════════════════════════════════════════════════════════════
    can_chat, reason = subscription_manager.can_use_chat(final_user_id, estimated_tokens= 150)  # Estimate tokens for limit check
    if not can_chat:
        raise HTTPException(status_code=429, detail=reason)
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 2: GET TIER AND LIMITS
    # ════════════════════════════════════════════════════════════════════
    sub = subscription_manager.get_subscription(final_user_id)
    tier = sub["tier"].value
    chat_limits = get_chat_limit(tier)
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 3: ENFORCE MESSAGE LENGTH LIMIT
    # ════════════════════════════════════════════════════════════════════
    user_message = body.message
    if len(user_message) > chat_limits["max_message_length"]:
        raise HTTPException(
            status_code=400,
            detail=f"Message too long. Max {chat_limits['max_message_length']} chars. Upgrade to Pro for longer messages."
        )
    
    # Build context window with memory
    context_messages = memory.get_context_window(
        session_id=session_id,
        system_prompt="",
        user_message=body.message,
    )
    context_messages = [m for m in context_messages if m.get("content")]

    if body.stream:
        async def event_stream():
            full_content = ""
            try:
                async for chunk in chat_service.chat_completion_stream(
                    context_messages,
                    model=body.model,
                    temperature=body.temperature,
                    max_tokens=chat_limits["max_tokens"],  # ENFORCE TIER LIMIT
                ):
                    full_content += chunk
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                
                # ════════════════════════════════════════════════════════════════════
                # SAVE USER MESSAGE TO DATABASE
                # ════════════════════════════════════════════════════════════════════
                user_message_tokens = estimate_tokens(body.message)
                await chat_storage.save_message(
                    db=db,
                    session_id=session_id,
                    user_identifier=final_user_id,
                    chatbot_id=body.session_id or "default",
                    role="user",
                    content=body.message,
                    tokens=user_message_tokens,
                )
                
                # Store in memory
                memory.add_turn(session_id, "user", body.message)
                memory.add_turn(session_id, "assistant", full_content)
                
                # ════════════════════════════════════════════════════════════════════
                # SAVE ASSISTANT MESSAGE TO DATABASE
                # ════════════════════════════════════════════════════════════════════
                assistant_message_tokens = estimate_tokens(full_content)
                await chat_storage.save_message(
                    db=db,
                    session_id=session_id,
                    user_identifier=final_user_id,
                    chatbot_id=body.session_id or "default",
                    role="assistant",
                    content=full_content,
                    tokens=assistant_message_tokens,
                )
                
                # ════════════════════════════════════════════════════════════════════
                # STEP 4: TRACK USAGE
                # ════════════════════════════════════════════════════════════════════
                tokens_used = user_message_tokens + assistant_message_tokens
                subscription_manager.add_chat_usage(final_user_id, tokens_used)
                stats = subscription_manager.get_usage_stats(final_user_id)
                
                # Track in database if authenticated
                if jwt_user:
                    await record_usage(
                        db=db,
                        user_id=jwt_user['user_id'],
                        service="chat",
                        tokens=tokens_used,
                    )
                
                # Send final stats
                yield f"data: {json.dumps({'type': 'done', 'content': full_content, 'usage': stats})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # Non-streaming response
    result = await chat_service.chat_completion(
        messages=context_messages,
        model=body.model,
        temperature=body.temperature,
        max_tokens=chat_limits["max_tokens"],  # ENFORCE TIER LIMIT
    )

    # ════════════════════════════════════════════════════════════════════
    # SAVE USER MESSAGE TO DATABASE
    # ════════════════════════════════════════════════════════════════════
    user_message_tokens = estimate_tokens(body.message)
    await chat_storage.save_message(
        db=db,
        session_id=session_id,
        user_identifier=final_user_id,
        chatbot_id=body.session_id or "default",
        role="user",
        content=body.message,
        tokens=user_message_tokens,
    )

    # Store in memory
    memory.add_turn(session_id, "user", body.message)
    memory.add_turn(session_id, "assistant", result["content"])

    # ════════════════════════════════════════════════════════════════════
    # SAVE ASSISTANT MESSAGE TO DATABASE
    # ════════════════════════════════════════════════════════════════════
    assistant_message_tokens = result.get("tokens", estimate_tokens(result["content"]))
    await chat_storage.save_message(
        db=db,
        session_id=session_id,
        user_identifier=final_user_id,
        chatbot_id=body.session_id or "default",
        role="assistant",
        content=result["content"],
        tokens=assistant_message_tokens,
    )

    # ════════════════════════════════════════════════════════════════════
    # STEP 5: TRACK USAGE
    # ════════════════════════════════════════════════════════════════════
    tokens_used = user_message_tokens + assistant_message_tokens
    subscription_manager.add_chat_usage(final_user_id, tokens_used)
    stats = subscription_manager.get_usage_stats(final_user_id)

    # Track in database if authenticated
    if jwt_user:
        await record_usage(
            db=db,
            user_id=jwt_user['user_id'],
            service="chat",
            tokens=tokens_used,
        )

    return ChatResponse(
        message=result["content"],
        tokens_used=tokens_used,
        session_id=session_id,
        latency_ms=result.get("latency_ms", 0.0),
        model=result.get("model", "gpt-4o-mini"),
        provider=result.get("provider", "openai"),
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
