"""
LLM Chat Service - supports Groq, OpenAI, and Google Gemini.
Handles streaming and non-streaming completions with latency tracking.

Provider routing:
  model starts with "groq/"             -> Groq (ultra-fast LPU inference)
  model starts with "gpt-", "o1", "o3"  -> OpenAI
  model starts with "gemini"            -> Google Gemini
  otherwise                             -> mock fallback
"""

import time
import asyncio
from typing import AsyncGenerator, Optional, List
from api.core.config import get_settings
from api.services.prompt_engine import get_system_prompt

settings = get_settings()

# --- Lazy clients ---
_openai_client = None
_groq_client = None
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


def _get_groq_client():
    global _groq_client
    if _groq_client is None:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=settings.GROQ_API_KEY)
        except ImportError:
            raise RuntimeError("groq package not installed. Run: pip install groq")
    return _groq_client


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


def _resolve_provider(model: str) -> str:
    """Determine which provider to use based on model name + available keys."""
    if model.startswith("groq/") and settings.GROQ_API_KEY:
        return "groq"
    if model.startswith(("gpt-", "o1", "o3")) and settings.OPENAI_API_KEY:
        return "openai"
    if model.startswith("gemini") and settings.GOOGLE_API_KEY:
        return "gemini"
    # Auto-fallback: try first available key
    if settings.GROQ_API_KEY:
        return "groq"
    if settings.OPENAI_API_KEY:
        return "openai"
    if settings.GOOGLE_API_KEY:
        return "gemini"
    return "mock"


# =============================================================
# NON-STREAMING COMPLETION
# =============================================================

async def chat_completion(
    messages: List[dict],
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
    prompt_template: Optional[str] = None,
    streaming: bool = False,
    emotion: str = "neutral",
) -> dict:
    """
    Non-streaming chat completion. Returns full response dict.
    """
    model = model or settings.DEFAULT_LLM_MODEL
    start = time.time()

    # Build system prompt via prompt engine
    sys_prompt = system_prompt or get_system_prompt(
        template_name=prompt_template or settings.DEFAULT_SYSTEM_PROMPT,
        streaming=streaming,
        emotion=emotion,
    )
    msgs = [{"role": "system", "content": sys_prompt}] + messages

    provider = _resolve_provider(model)

    # -- Groq --
    if provider == "groq":
        client = _get_groq_client()
        groq_model = model.replace("groq/", "") if model.startswith("groq/") else model
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=groq_model,
            messages=msgs,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=1,
            stream=False,
            stop=None,
        )
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0
        latency = (time.time() - start) * 1000
        return {
            "content": content,
            "tokens": tokens,
            "latency_ms": round(latency, 1),
            "model": groq_model,
            "provider": "groq",
        }

    # -- OpenAI --
    if provider == "openai":
        client = _get_openai_client()
        response = await client.chat.completions.create(
            model=model,
            messages=msgs,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0
        latency = (time.time() - start) * 1000
        return {
            "content": content,
            "tokens": tokens,
            "latency_ms": round(latency, 1),
            "model": model,
            "provider": "openai",
        }

    # -- Google Gemini --
    if provider == "gemini":
        gemini = _get_gemini_model(model)
        prompt_parts = []
        for msg in msgs:
            role = msg.get("role", "user")
            prefix = "" if role == "user" else f"[{role}] "
            prompt_parts.append(f"{prefix}{msg['content']}")
        prompt = "\n".join(prompt_parts)
        response = await asyncio.to_thread(gemini.generate_content, prompt)
        latency = (time.time() - start) * 1000
        return {
            "content": response.text,
            "tokens": 0,
            "latency_ms": round(latency, 1),
            "model": model,
            "provider": "gemini",
        }

    # -- Mock fallback --
    user_msg = messages[-1]["content"] if messages else ""
    latency = (time.time() - start) * 1000
    return {
        "content": (
            f"[Athena AI] I received: \"{user_msg}\". "
            f"Configure GROQ_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY in .env."
        ),
        "tokens": 0,
        "latency_ms": round(latency, 1),
        "model": "mock",
        "provider": "mock",
    }


# =============================================================
# STREAMING COMPLETION
# =============================================================

async def chat_completion_stream(
    messages: List[dict],
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
    prompt_template: Optional[str] = None,
    emotion: str = "neutral",
) -> AsyncGenerator[str, None]:
    """
    Streaming chat completion. Yields text chunks for real-time TTS pipeline.
    Optimised for low-latency: sends tokens as they arrive.
    """
    model = model or settings.DEFAULT_LLM_MODEL

    # Build system prompt with streaming optimisation
    sys_prompt = system_prompt or get_system_prompt(
        template_name=prompt_template or settings.DEFAULT_SYSTEM_PROMPT,
        streaming=True,
        emotion=emotion,
    )
    msgs = [{"role": "system", "content": sys_prompt}] + messages

    provider = _resolve_provider(model)

    # -- Groq Streaming --
    if provider == "groq":
        client = _get_groq_client()
        groq_model = model.replace("groq/", "") if model.startswith("groq/") else model

        def _groq_stream():
            return client.chat.completions.create(
                model=groq_model,
                messages=msgs,
                temperature=temperature,
                max_completion_tokens=max_tokens,
                top_p=1,
                stream=True,
                stop=None,
            )

        stream = await asyncio.to_thread(_groq_stream)
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
        return

    # -- OpenAI Streaming --
    if provider == "openai":
        client = _get_openai_client()
        stream = await client.chat.completions.create(
            model=model,
            messages=msgs,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
        return

    # -- Gemini (no native streaming - simulate) --
    if provider == "gemini":
        result = await chat_completion(messages, model, temperature, max_tokens, system_prompt)
        for word in result["content"].split():
            yield word + " "
            await asyncio.sleep(0.02)
        return

    # -- Mock streaming fallback --
    user_msg = messages[-1]["content"] if messages else ""
    mock_text = (
        f"I received your message: \"{user_msg}\". "
        f"Configure GROQ_API_KEY in .env for ultra-fast AI responses."
    )
    for word in mock_text.split():
        yield word + " "
        await asyncio.sleep(0.04)


# =============================================================
# SENTENCE-CHUNKED STREAMING (for TTS pipeline)
# =============================================================

async def stream_sentences(
    messages: List[dict],
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Yields complete sentences from the LLM stream.
    Better for TTS - each yield is a speakable chunk.
    Sentence boundaries: . ! ? and newlines.
    """
    buffer = ""
    async for token in chat_completion_stream(
        messages, model, temperature, max_tokens, system_prompt
    ):
        buffer += token
        # Check for sentence boundaries
        while any(sep in buffer for sep in [". ", "! ", "? ", ".\n", "!\n", "?\n"]):
            for sep in [". ", "! ", "? ", ".\n", "!\n", "?\n"]:
                idx = buffer.find(sep)
                if idx != -1:
                    sentence = buffer[:idx + 1].strip()
                    buffer = buffer[idx + len(sep):]
                    if sentence:
                        yield sentence
                    break

    # Flush remaining buffer
    if buffer.strip():
        yield buffer.strip()


def get_available_providers() -> List[dict]:
    """Return which LLM providers are configured."""
    providers = []
    if settings.GROQ_API_KEY:
        providers.append({"id": "groq", "name": "Groq (LPU)", "status": "active"})
    if settings.OPENAI_API_KEY:
        providers.append({"id": "openai", "name": "OpenAI", "status": "active"})
    if settings.GOOGLE_API_KEY:
        providers.append({"id": "gemini", "name": "Google Gemini", "status": "active"})
    if not providers:
        providers.append({"id": "mock", "name": "Mock (Demo)", "status": "active"})
    return providers
