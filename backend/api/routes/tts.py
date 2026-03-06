"""
TTS routes — text-to-speech synthesis with streaming and voice management.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import io

from api.schemas.schemas import TTSRequest, TTSResponse
from api.services import tts_service

router = APIRouter(tags=["Text-to-Speech"])


@router.post("/api/tts")
async def text_to_speech(body: TTSRequest):
    """Convert text to speech audio."""
    if not tts_service.is_available():
        raise HTTPException(status_code=503, detail="TTS not available. Install edge-tts.")

    result = await tts_service.synthesize_speech(
        text=body.text,
        voice=body.voice,
        speed=body.speed,
        pitch=body.pitch,
        return_base64=body.base64,
    )

    if body.base64:
        return TTSResponse(**result)

    # Return audio stream
    return StreamingResponse(
        io.BytesIO(result["audio_bytes"]),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=speech.mp3"},
    )


@router.post("/v1/tts")
async def tts_api(body: TTSRequest):
    """Developer API: text-to-speech."""
    return await text_to_speech(body)


@router.get("/api/tts/voices")
async def list_voices(locale: str = "en"):
    """List available TTS voices."""
    if not tts_service.is_available():
        raise HTTPException(status_code=503, detail="TTS not available")

    voices = await tts_service.list_voices(locale_filter=locale)
    return {"voices": voices, "default": "en-US-GuyNeural"}


@router.get("/api/tts/voices/categories")
async def get_voice_categories():
    """Get organised voice categories (male/female) for the UI."""
    return tts_service.get_voice_categories()


@router.post("/api/tts/stream")
async def stream_tts(body: TTSRequest):
    """Stream TTS audio chunks for real-time playback (200-400ms target)."""
    if not tts_service.is_available():
        raise HTTPException(status_code=503, detail="TTS not available")

    async def audio_stream():
        async for chunk in tts_service.stream_speech(
            body.text, body.voice, speed=body.speed, pitch=body.pitch
        ):
            yield chunk

    return StreamingResponse(audio_stream(), media_type="audio/mpeg")
