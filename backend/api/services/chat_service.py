"""
LLM Chat Service — supports OpenAI and Google Gemini.
Handles streaming and non-streaming completions.
"""

import time
import asyncio
from typing import AsyncGenerator, Optional, List
from api.core.config import get_settings

settings = get_settings()

# Lazy imports
_openai_client = None
_gemini_model = None


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        try:
            from openai import AsyncOpenAI
            _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        except ImportError:
            raise RuntimeError("openai package not installed. Run: pip install openai")
    return _openai_client


def _get_gemini_model(model_name: str = "gemini-pro"):
    global _gemini_model
    if _gemini_model is None:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            _gemini_model = genai.GenerativeModel(model_name)
        except ImportError:
            raise RuntimeError("google-generativeai package not installed.")
    return _gemini_model


async def chat_completion(
    messages: List[dict],
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
) -> dict:
    """
    Non-streaming chat completion. Returns full response.
    Falls back to mock if no API key is configured.
    """
    start = time.time()

    # Prepend system prompt if provided
    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages

    # ── OpenAI ───────────────────────────────────
    if settings.OPENAI_API_KEY and model.startswith(("gpt-", "o1", "o3")):
        client = _get_openai_client()
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0
        latency = (time.time() - start) * 1000
        return {"content": content, "tokens": tokens, "latency_ms": latency, "model": model}

    # ── Google Gemini ────────────────────────────
    if settings.GOOGLE_API_KEY and model.startswith("gemini"):
        gemini = _get_gemini_model(model)
        # Convert OpenAI format to Gemini format
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            prefix = "" if role == "user" else f"[{role}] "
            prompt_parts.append(f"{prefix}{msg['content']}")
        prompt = "\n".join(prompt_parts)
        response = await asyncio.to_thread(gemini.generate_content, prompt)
        latency = (time.time() - start) * 1000
        return {"content": response.text, "tokens": 0, "latency_ms": latency, "model": model}

    # ── Mock fallback ────────────────────────────
    user_msg = messages[-1]["content"] if messages else ""
    latency = (time.time() - start) * 1000
    return {
        "content": f"[Athena AI] I received your message: \"{user_msg}\". "
                   f"Configure OPENAI_API_KEY or GOOGLE_API_KEY in .env to enable real AI responses.",
        "tokens": 0,
        "latency_ms": latency,
        "model": "mock",
    }


async def chat_completion_stream(
    messages: List[dict],
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Streaming chat completion. Yields text chunks.
    """
    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages

    # ── OpenAI Streaming ─────────────────────────
    if settings.OPENAI_API_KEY and model.startswith(("gpt-", "o1", "o3")):
        client = _get_openai_client()
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
        return

    # ── Mock streaming fallback ──────────────────
    user_msg = messages[-1]["content"] if messages else ""
    mock_text = (
        f"I received your message: \"{user_msg}\". "
        f"Configure an API key in .env for real AI responses."
    )
    for word in mock_text.split():
        yield word + " "
        await asyncio.sleep(0.05)
