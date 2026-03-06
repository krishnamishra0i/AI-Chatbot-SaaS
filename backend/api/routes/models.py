"""
Models & Providers info endpoint — /v1/models, /api/providers, /api/prompts
"""

from fastapi import APIRouter

from api.services.chat_service import get_available_providers
from api.services.prompt_engine import list_templates

router = APIRouter(tags=["Models"])


AVAILABLE_MODELS = [
    # --- Groq (ultra-fast LPU inference) ---
    {
        "id": "groq/llama-3.3-70b-versatile",
        "name": "Llama 3.3 70B",
        "provider": "groq",
        "max_tokens": 32768,
        "supports_streaming": True,
        "description": "Fast, high-quality open model via Groq LPU",
    },
    {
        "id": "groq/llama-3.1-8b-instant",
        "name": "Llama 3.1 8B Instant",
        "provider": "groq",
        "max_tokens": 8192,
        "supports_streaming": True,
        "description": "Ultra-fast, lightweight model for quick responses",
    },
    {
        "id": "groq/mixtral-8x7b-32768",
        "name": "Mixtral 8x7B",
        "provider": "groq",
        "max_tokens": 32768,
        "supports_streaming": True,
        "description": "Mixture of experts model, great for complex tasks",
    },
    {
        "id": "groq/gemma2-9b-it",
        "name": "Gemma 2 9B",
        "provider": "groq",
        "max_tokens": 8192,
        "supports_streaming": True,
        "description": "Google's Gemma 2 via Groq, fast inference",
    },
    # --- OpenAI ---
    {
        "id": "gpt-3.5-turbo",
        "name": "GPT-3.5 Turbo",
        "provider": "openai",
        "max_tokens": 4096,
        "supports_streaming": True,
        "description": "Fast and cost-effective",
    },
    {
        "id": "gpt-4",
        "name": "GPT-4",
        "provider": "openai",
        "max_tokens": 8192,
        "supports_streaming": True,
        "description": "Most capable OpenAI model",
    },
    {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "provider": "openai",
        "max_tokens": 128000,
        "supports_streaming": True,
        "description": "Fastest GPT-4 class model",
    },
    # --- Google Gemini ---
    {
        "id": "gemini-pro",
        "name": "Gemini Pro",
        "provider": "google",
        "max_tokens": 8192,
        "supports_streaming": True,
        "description": "Google's flagship model",
    },
    {
        "id": "gemini-1.5-pro",
        "name": "Gemini 1.5 Pro",
        "provider": "google",
        "max_tokens": 1048576,
        "supports_streaming": True,
        "description": "1M context window",
    },
]


@router.get("/v1/models")
async def list_models():
    """List all available LLM models."""
    return {"object": "list", "data": AVAILABLE_MODELS}


@router.get("/api/providers")
async def list_providers():
    """List configured LLM providers and their status."""
    return {"providers": get_available_providers()}


@router.get("/api/prompts")
async def list_prompts():
    """List available system prompt templates."""
    return {"templates": list_templates()}
