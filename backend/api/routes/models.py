"""
Models info endpoint — /v1/models
"""

from fastapi import APIRouter

router = APIRouter(tags=["Models"])


AVAILABLE_MODELS = [
    {
        "id": "gpt-3.5-turbo",
        "name": "GPT-3.5 Turbo",
        "provider": "openai",
        "max_tokens": 4096,
        "supports_streaming": True,
    },
    {
        "id": "gpt-4",
        "name": "GPT-4",
        "provider": "openai",
        "max_tokens": 8192,
        "supports_streaming": True,
    },
    {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "provider": "openai",
        "max_tokens": 128000,
        "supports_streaming": True,
    },
    {
        "id": "gemini-pro",
        "name": "Gemini Pro",
        "provider": "google",
        "max_tokens": 8192,
        "supports_streaming": True,
    },
    {
        "id": "gemini-1.5-pro",
        "name": "Gemini 1.5 Pro",
        "provider": "google",
        "max_tokens": 1048576,
        "supports_streaming": True,
    },
]


@router.get("/v1/models")
async def list_models():
    """List available LLM models."""
    return {"object": "list", "data": AVAILABLE_MODELS}
