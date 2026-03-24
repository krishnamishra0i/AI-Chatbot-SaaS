"""
TTS routes — text-to-speech synthesis with streaming and voice management + subscription limits.
"""

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
import io
import logging

from api.schemas.schemas import TTSRequest, TTSResponse
from api.services import tts_service
from api.services import tts_service_openai
from api.services.subscription_manager import subscription_manager
from api.services.optimization_config import get_tts_limit

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Text-to-Speech"])


def _as_openai_speed(value) -> float:
    """Normalize speed input for OpenAI TTS API."""
    if value is None:
        return 1.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        # Accept legacy strings such as "1.0".
        return float(str(value).strip())
    except (TypeError, ValueError):
        return 1.0


def _as_legacy_voice_param(value, default_value: str) -> str:
    """Normalize speed/pitch for legacy edge-tts style parameters."""
    if value is None:
        return default_value
    if isinstance(value, (int, float)):
        return str(value)
    string_value = str(value).strip()
    return string_value or default_value


@router.post("/api/tts")
async def text_to_speech(
    body: TTSRequest,
    user_id: str = Header(None),
):
    """Convert text to speech audio with subscription limits."""
    if not tts_service.is_available():
        raise HTTPException(status_code=503, detail="TTS not available. Install openai package.")

    final_user_id = user_id or "demo"
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 1: ESTIMATE TTS DURATION
    # ════════════════════════════════════════════════════════════════════
    # Rough formula: 150 characters per 5 seconds
    estimated_seconds = max(0.5, (len(body.text) / 150) * 5)
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 2: CHECK SUBSCRIPTION LIMITS
    # ════════════════════════════════════════════════════════════════════
    can_tts, reason = subscription_manager.can_use_tts(final_user_id, estimated_seconds)
    if not can_tts:
        raise HTTPException(status_code=429, detail=reason)
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 3: GET TIER AND LIMITS
    # ════════════════════════════════════════════════════════════════════
    sub = subscription_manager.get_subscription(final_user_id)
    tier = sub["tier"].value
    tts_limits = get_tts_limit(tier)
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 4: ENFORCE CHARACTER LIMIT
    # ════════════════════════════════════════════════════════════════════
    if len(body.text) > tts_limits["max_chars"]:
        raise HTTPException(
            status_code=400,
            detail=f"Text too long for TTS. Max {tts_limits['max_chars']} chars (Demo: 500, Starter: 2K, Pro: 5K). Upgrade to continue."
        )
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 5: SYNTHESIZE SPEECH
    # ════════════════════════════════════════════════════════════════════
    result = await tts_service.synthesize_speech(
        text=body.text,
        voice=body.voice,
        speed=_as_legacy_voice_param(body.speed, "normal"),
        pitch=_as_legacy_voice_param(body.pitch, "default"),
        return_base64=body.base64,
    )
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 6: TRACK TTS USAGE
    # ════════════════════════════════════════════════════════════════════
    subscription_manager.add_tts_usage(final_user_id, estimated_seconds)
    stats = subscription_manager.get_usage_stats(final_user_id)
    
    if body.base64:
        result["metadata"] = {
            "tts_seconds_used": estimated_seconds,
            "tts_remaining_seconds": stats["tts_remaining_seconds"],
            "session_time_remaining": stats["session_time_remaining"],
            "tier": tier,
        }
        return TTSResponse(**result)

    # Return audio stream with metadata
    response = StreamingResponse(
        io.BytesIO(result["audio_bytes"]),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=speech.mp3",
            "X-TTS-Duration": str(estimated_seconds),
            "X-TTS-Remaining": str(stats["tts_remaining_seconds"]),
            "X-Session-Remaining": str(stats["session_time_remaining"]),
        },
    )
    return response


@router.post("/v1/tts")
async def tts_api(
    body: TTSRequest,
    user_id: str = Header(None),
):
    """Developer API: text-to-speech."""
    return await text_to_speech(body, user_id)


@router.get("/api/tts/voices")
async def list_voices(
    locale: str = "en",
    user_id: str = Header(None),
):
    """List available TTS voices (subscription protected)."""
    if not tts_service.is_available():
        raise HTTPException(status_code=503, detail="TTS not available")
    
    final_user_id = user_id or "demo"
    
    # Check if user can access TTS features
    can_tts, reason = subscription_manager.can_use_tts(final_user_id, 0.1)
    if not can_tts:
        raise HTTPException(status_code=429, detail=reason)

    voices = await tts_service.list_voices(locale_filter=locale)
    return {"voices": voices, "default": "alloy"}


@router.get("/api/tts/voices/categories")
async def get_voice_categories(user_id: str = Header(None)):
    """Get organised voice categories (male/female) for the UI."""
    final_user_id = user_id or "demo"
    
    # Check if user can access TTS features
    can_tts, reason = subscription_manager.can_use_tts(final_user_id, 0.1)
    if not can_tts:
        raise HTTPException(status_code=429, detail=reason)
    
    return tts_service.get_voice_categories()


@router.post("/api/tts/stream")
async def stream_tts(body: TTSRequest):
    """Stream TTS audio chunks for real-time playback (200-400ms target)."""
    if not tts_service.is_available():
        raise HTTPException(status_code=503, detail="TTS not available")

    async def audio_stream():
        async for chunk in tts_service.stream_speech(
            body.text,
            body.voice,
            speed=_as_legacy_voice_param(body.speed, "normal"),
            pitch=_as_legacy_voice_param(body.pitch, "default"),
        ):
            yield chunk

    return StreamingResponse(audio_stream(), media_type="audio/mpeg")


# ════════════════════════════════════════════════════════════════════
# ⚡ REAL-TIME OPTIMIZED TTS ENDPOINTS (using OpenAI API)
# ════════════════════════════════════════════════════════════════════

@router.post("/api/tts/realtime/stream", tags=["Text-to-Speech"])
async def realtime_tts_stream(
    body: TTSRequest,
    user_id: str = Header(None),
):
    """
    ⚡ Real-time optimized TTS streaming.
    
    Streams audio chunks immediately for sub-100ms latency.
    Perfect for concurrent STT/TTS in real-time conversations.
    
    Returns: Streaming MP3 audio chunks
    """
    if not tts_service_openai.is_available():
        raise HTTPException(status_code=503, detail="TTS not available")

    final_user_id = user_id or "demo"
    
    # Check subscription limits
    estimated_seconds = max(0.5, (len(body.text) / 150) * 5)
    can_tts, reason = subscription_manager.can_use_tts(final_user_id, estimated_seconds)
    if not can_tts:
        raise HTTPException(status_code=429, detail=reason)
    
    # Track usage
    subscription_manager.add_tts_usage(final_user_id, estimated_seconds)
    
    async def audio_stream():
        """Stream TTS chunks from OpenAI."""
        try:
            logger.debug(f"Streaming TTS: {len(body.text)} chars, voice={body.voice or 'nova'}")
            
            async for chunk in tts_service_openai.synthesize_speech_stream(
                text=body.text,
                voice=body.voice or "nova",
                speed=_as_openai_speed(body.speed),
            ):
                yield chunk
        
        except Exception as e:
            logger.error(f"TTS streaming failed: {e}")
            raise
    
    return StreamingResponse(
        audio_stream(),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=speech.mp3",
            "X-TTS-Duration": str(estimated_seconds),
        }
    )


@router.post("/api/tts/realtime/base64", tags=["Text-to-Speech"])
async def realtime_tts_base64(
    body: TTSRequest,
    user_id: str = Header(None),
):
    """
    ⚡ Real-time TTS returning complete base64 audio.
    
    Use when you need the complete audio data at once
    (e.g., for pre-buffering before playback).
    
    Returns: { audio: "base64_encoded_mp3" }
    """
    if not tts_service_openai.is_available():
        raise HTTPException(status_code=503, detail="TTS not available")
    
    final_user_id = user_id or "demo"
    
    # Check subscription
    estimated_seconds = max(0.5, (len(body.text) / 150) * 5)
    can_tts, reason = subscription_manager.can_use_tts(final_user_id, estimated_seconds)
    if not can_tts:
        raise HTTPException(status_code=429, detail=reason)
    
    try:
        # Synthesize
        audio_base64 = await tts_service_openai.synthesize_speech_base64(
            text=body.text,
            voice=body.voice or "nova",
            speed=_as_openai_speed(body.speed),
        )
        
        # Track usage
        subscription_manager.add_tts_usage(final_user_id, estimated_seconds)
        stats = subscription_manager.get_usage_stats(final_user_id)
        
        return {
            "audio": audio_base64,
            "voice": body.voice or "nova",
            "duration_estimated": estimated_seconds,
            "metadata": {
                "tts_seconds_used": estimated_seconds,
                "tts_remaining_seconds": stats["tts_remaining_seconds"],
            }
        }
    
    except Exception as e:
        logger.error(f"TTS base64 failed: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


@router.get("/api/tts/realtime/voices", tags=["Text-to-Speech"])
async def realtime_tts_voices(user_id: str = Header(None)):
    """Get available real-time TTS voices (OpenAI)."""
    if not tts_service_openai.is_available():
        raise HTTPException(status_code=503, detail="TTS not available")
    
    final_user_id = user_id or "demo"
    can_tts, reason = subscription_manager.can_use_tts(final_user_id, 0.1)
    if not can_tts:
        raise HTTPException(status_code=429, detail=reason)
    
    return {
        "voices": tts_service_openai.get_voices(),
        "default": "nova",
        "model": "tts-1",
        "latency_ms": "50-200"
    }
