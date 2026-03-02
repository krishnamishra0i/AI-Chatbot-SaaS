"""
Text-to-Speech service using edge-tts.
Supports streaming audio and voice listing.
"""

import asyncio
import base64
import io
from typing import Optional, List

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
    voice: str = "en-US-GuyNeural",
    return_base64: bool = False,
) -> dict:
    """
    Convert text to speech. Returns audio bytes or base64 string.
    """
    if not EDGE_TTS_AVAILABLE:
        raise RuntimeError("edge-tts not installed. Run: pip install edge-tts")

    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]

    if return_base64:
        return {
            "audio": base64.b64encode(audio_data).decode("utf-8"),
            "format": "mp3",
            "voice": voice,
        }

    return {"audio_bytes": audio_data, "format": "mp3", "voice": voice}


async def stream_speech(text: str, voice: str = "en-US-GuyNeural"):
    """
    Generator: yields audio chunks for streaming playback.
    """
    if not EDGE_TTS_AVAILABLE:
        raise RuntimeError("edge-tts not installed")

    communicate = edge_tts.Communicate(text, voice)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]


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


def is_available() -> bool:
    return EDGE_TTS_AVAILABLE
