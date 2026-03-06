"""
Text-to-Speech service using edge-tts.
Supports streaming audio chunks, voice listing, speed/pitch control.
Optimised for real-time avatar pipeline (200-400ms chunks).
"""

import asyncio
import base64
import io
import time
from typing import Optional, List, AsyncGenerator

from api.core.config import get_settings

settings = get_settings()

# Module availability flag
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False


async def synthesize_speech(
    text: str,
    voice: str = None,
    speed: str = None,
    pitch: str = None,
    return_base64: bool = False,
) -> dict:
    """
    Convert text to speech. Returns audio bytes or base64 string.
    """
    if not EDGE_TTS_AVAILABLE:
        raise RuntimeError("edge-tts not installed. Run: pip install edge-tts")

    voice = voice or settings.TTS_VOICE
    speed = speed or settings.TTS_SPEED
    pitch = pitch or settings.TTS_PITCH

    communicate = edge_tts.Communicate(text, voice, rate=speed, pitch=pitch)
    audio_data = b""
    start = time.time()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]

    latency_ms = (time.time() - start) * 1000

    if return_base64:
        return {
            "audio": base64.b64encode(audio_data).decode("utf-8"),
            "format": "mp3",
            "voice": voice,
            "latency_ms": round(latency_ms, 1),
            "size_bytes": len(audio_data),
        }

    return {
        "audio_bytes": audio_data,
        "format": "mp3",
        "voice": voice,
        "latency_ms": round(latency_ms, 1),
        "size_bytes": len(audio_data),
    }


async def stream_speech(
    text: str,
    voice: str = None,
    speed: str = None,
    pitch: str = None,
) -> AsyncGenerator[bytes, None]:
    """
    Generator: yields audio chunks for real-time streaming.
    Target: 200-400ms chunks for low-latency lip sync.
    """
    if not EDGE_TTS_AVAILABLE:
        raise RuntimeError("edge-tts not installed")

    voice = voice or settings.TTS_VOICE
    speed = speed or settings.TTS_SPEED
    pitch = pitch or settings.TTS_PITCH

    communicate = edge_tts.Communicate(text, voice, rate=speed, pitch=pitch)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]


async def stream_speech_for_sentences(
    sentences: AsyncGenerator[str, None],
    voice: str = None,
    speed: str = None,
) -> AsyncGenerator[dict, None]:
    """
    Takes an async generator of sentences (from LLM stream)
    and yields audio chunks with metadata for each sentence.
    
    This is the core of the real-time pipeline:
      LLM stream -> sentence chunks -> TTS audio -> lip sync
    """
    voice = voice or settings.TTS_VOICE
    speed = speed or settings.TTS_SPEED

    async for sentence in sentences:
        start = time.time()
        audio_data = b""

        communicate = edge_tts.Communicate(sentence, voice, rate=speed)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
                # Yield partial audio for truly low-latency playback
                if len(audio_data) > 4096:
                    yield {
                        "type": "audio_chunk",
                        "data": audio_data,
                        "sentence": sentence,
                        "partial": True,
                    }
                    audio_data = b""

        if audio_data:
            yield {
                "type": "audio_chunk",
                "data": audio_data,
                "sentence": sentence,
                "partial": False,
                "latency_ms": round((time.time() - start) * 1000, 1),
            }


async def list_voices(locale_filter: Optional[str] = "en") -> List[dict]:
    """
    List available TTS voices, optionally filtered by locale prefix.
    """
    if not EDGE_TTS_AVAILABLE:
        raise RuntimeError("edge-tts not installed")

    voices = await edge_tts.list_voices()

    if locale_filter:
        voices = [v for v in voices if v.get("Locale", "").startswith(locale_filter)]

    return [
        {
            "name": v.get("FriendlyName", ""),
            "short_name": v.get("ShortName", ""),
            "locale": v.get("Locale", ""),
            "gender": v.get("Gender", ""),
        }
        for v in voices
    ]


def get_voice_categories() -> dict:
    """Return voice categories for the UI."""
    return {
        "male": [
            {"id": "en-US-GuyNeural", "name": "Guy (US Male)"},
            {"id": "en-US-ChristopherNeural", "name": "Christopher (US Male)"},
            {"id": "en-GB-RyanNeural", "name": "Ryan (UK Male)"},
            {"id": "en-AU-WilliamNeural", "name": "William (AU Male)"},
        ],
        "female": [
            {"id": "en-US-JennyNeural", "name": "Jenny (US Female)"},
            {"id": "en-US-AriaNeural", "name": "Aria (US Female)"},
            {"id": "en-GB-SoniaNeural", "name": "Sonia (UK Female)"},
            {"id": "en-AU-NatashaNeural", "name": "Natasha (AU Female)"},
        ],
    }


def is_available() -> bool:
    return EDGE_TTS_AVAILABLE
