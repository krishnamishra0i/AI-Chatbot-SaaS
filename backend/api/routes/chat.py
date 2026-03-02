"""
Chat routes — /api/chat and /v1/chat/completions (OpenAI-compatible).
"""

import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.core.config import get_settings
from api.schemas.schemas import ChatRequest, ChatResponse, ChatCompletionRequest
from api.services import chat_service

settings = get_settings()
router = APIRouter(tags=["Chat"])


@router.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Simple chat endpoint for the frontend chatbot."""
    messages = [{"role": "user", "content": body.message}]

    if body.stream:
        # Return SSE stream
        async def event_stream():
            async for chunk in chat_service.chat_completion_stream(messages):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    result = await chat_service.chat_completion(
        messages=messages,
        system_prompt=settings.DEFAULT_SYSTEM_PROMPT,
    )

    return ChatResponse(
        message=result["content"],
        session_id="default",
        tokens_used=result.get("tokens", 0),
        latency_ms=result.get("latency_ms", 0),
        timestamp=datetime.now(timezone.utc),
    )


@router.post("/v1/chat/completions")
async def chat_completions(body: ChatCompletionRequest):
    """
    OpenAI-compatible /v1/chat/completions endpoint.
    Supports streaming via SSE.
    """
    if body.stream:
        async def event_stream():
            import json
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
