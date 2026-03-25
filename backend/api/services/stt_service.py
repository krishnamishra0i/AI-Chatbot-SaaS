"""
Speech-to-Text service using OpenAI Whisper.
"""

import os
import tempfile
import base64
import asyncio
from typing import Optional
from pathlib import Path

from api.core.config import get_settings

settings = get_settings()

# Module availability flag
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

_model = None


def _get_model():
    global _model
    if _model is None:
        if not WHISPER_AVAILABLE:
            raise RuntimeError("openai-whisper not installed. Run: pip install openai-whisper")
        _model = whisper.load_model(settings.WHISPER_MODEL)
    return _model


async def transcribe_audio(
    audio_bytes: Optional[bytes] = None,
    audio_base64: Optional[str] = None,
    file_path: Optional[str] = None,
    file_suffix: Optional[str] = None,
) -> dict:
    """
    Transcribe audio to text. Accepts bytes, base64, or file path.
    """
    temp_path = None
    try:
        if audio_base64:
            audio_bytes = base64.b64decode(audio_base64)

        if audio_bytes:
            suffix = file_suffix if file_suffix and file_suffix.startswith(".") else ".webm"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(audio_bytes)
                temp_path = tmp.name
            file_path = temp_path

        # If a file path is provided, infer suffix for logging/debug if needed.
        if file_path and not file_suffix:
            file_suffix = Path(file_path).suffix

        if not file_path:
            raise ValueError("No audio data provided")

        model = _get_model()
        result = await asyncio.to_thread(model.transcribe, file_path)
        raw_text = result.get("text", "")
        normalized_text: str = raw_text if isinstance(raw_text, str) else ""

        return {
            "text": normalized_text.strip(),
            "language": result.get("language", "en"),
            "segments": result.get("segments", []),
        }
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def get_info() -> dict:
    return {
        "available": WHISPER_AVAILABLE,
        "model": settings.WHISPER_MODEL,
        "supported_formats": ["wav", "mp3", "ogg", "flac", "m4a", "webm"],
    }


def is_available() -> bool:
    return WHISPER_AVAILABLE
