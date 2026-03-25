"""
STT routes — speech-to-text transcription with subscription limits.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from pydantic import BaseModel
from typing import Optional
from pathlib import Path

from api.schemas.schemas import STTResponse
from api.services import stt_service
from api.services.subscription_manager import subscription_manager
from api.services.optimization_config import get_stt_limit

router = APIRouter(tags=["Speech-to-Text"])


class STTBase64Request(BaseModel):
    audio: str  # base64-encoded audio


def estimate_audio_duration(audio_bytes: bytes, sample_rate: int = 16000) -> float:
    """Estimate audio duration in seconds."""
    # Formula: duration = (bytes / (sample_rate * channels * bytes_per_sample))
    # Assuming 16-bit mono: 2 bytes per sample
    bytes_per_second = sample_rate * 2
    return len(audio_bytes) / bytes_per_second


@router.post("/api/stt", response_model=STTResponse)
async def speech_to_text(
    file: Optional[UploadFile] = File(None),
    user_id: str = Header(None),
):
    """
    Convert speech to text via file upload (multipart) with subscription limits.
    """
    if not stt_service.is_available():
        raise HTTPException(status_code=503, detail="STT not available. Install openai-whisper.")

    if not file:
        raise HTTPException(status_code=400, detail="Provide audio file")

    final_user_id = user_id or "demo"
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 1: READ AUDIO FILE
    # ════════════════════════════════════════════════════════════════════
    audio_bytes = await file.read()
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 2: ESTIMATE DURATION
    # ════════════════════════════════════════════════════════════════════
    estimated_seconds = estimate_audio_duration(audio_bytes)
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 3: CHECK SUBSCRIPTION LIMITS
    # ════════════════════════════════════════════════════════════════════
    can_stt, reason = subscription_manager.can_use_stt(final_user_id, estimated_seconds)
    if not can_stt:
        raise HTTPException(status_code=429, detail=reason)
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 4: GET TIER AND LIMITS
    # ════════════════════════════════════════════════════════════════════
    sub = subscription_manager.get_subscription(final_user_id)
    tier = sub["tier"].value
    stt_limits = get_stt_limit(tier)
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 5: ENFORCE DURATION LIMIT
    # ════════════════════════════════════════════════════════════════════
    if estimated_seconds > stt_limits["max_duration_seconds"]:
        raise HTTPException(
            status_code=400,
            detail=f"Audio too long. Max {stt_limits['max_duration_seconds']}s. Upgrade to Pro for longer recordings."
        )
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 6: TRANSCRIBE AUDIO
    # ════════════════════════════════════════════════════════════════════
    suffix = Path(file.filename or "").suffix.lower() if file.filename else ""
    if not suffix:
        # Handle browser recorder uploads that may omit filename extension
        content_type = (file.content_type or "").lower()
        if "webm" in content_type:
            suffix = ".webm"
        elif "ogg" in content_type:
            suffix = ".ogg"
        elif "mpeg" in content_type or "mp3" in content_type:
            suffix = ".mp3"
        elif "wav" in content_type:
            suffix = ".wav"

    result = await stt_service.transcribe_audio(audio_bytes=audio_bytes, file_suffix=suffix or ".webm")
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 7: TRACK STT USAGE
    # ════════════════════════════════════════════════════════════════════
    subscription_manager.add_stt_usage(final_user_id, estimated_seconds)
    stats = subscription_manager.get_usage_stats(final_user_id)
    
    # Add usage metadata to response
    result["metadata"] = {
        "stt_seconds_used": estimated_seconds,
        "stt_remaining_seconds": stats["stt_remaining_seconds"],
        "session_time_remaining": stats["session_time_remaining"],
        "tier": tier,
    }
    
    return STTResponse(**result)


@router.post("/api/stt/base64", response_model=STTResponse)
async def speech_to_text_base64(
    body: STTBase64Request,
    user_id: str = Header(None),
):
    """Convert speech to text via base64 JSON body with subscription limits."""
    if not stt_service.is_available():
        raise HTTPException(status_code=503, detail="STT not available. Install openai-whisper.")

    final_user_id = user_id or "demo"
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 1: DECODE BASE64 AND ESTIMATE DURATION
    # ════════════════════════════════════════════════════════════════════
    result = await stt_service.transcribe_audio(audio_base64=body.audio)
    
    # Estimate from base64 length (roughly: base64 is 4/3 of binary size)
    binary_size = len(body.audio) * 3 / 4
    estimated_seconds = estimate_audio_duration(b"x" * int(binary_size))
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 2: CHECK SUBSCRIPTION LIMITS
    # ════════════════════════════════════════════════════════════════════
    can_stt, reason = subscription_manager.can_use_stt(final_user_id, estimated_seconds)
    if not can_stt:
        raise HTTPException(status_code=429, detail=reason)
    
    # ════════════════════════════════════════════════════════════════════
    # STEP 3: TRACK STT USAGE
    # ════════════════════════════════════════════════════════════════════
    subscription_manager.add_stt_usage(final_user_id, estimated_seconds)
    stats = subscription_manager.get_usage_stats(final_user_id)
    
    result["metadata"] = {
        "stt_seconds_used": estimated_seconds,
        "stt_remaining_seconds": stats["stt_remaining_seconds"],
        "session_time_remaining": stats["session_time_remaining"],
    }
    
    return STTResponse(**result)


@router.post("/api/stt/upload", response_model=STTResponse)
async def stt_upload(
    audio: UploadFile = File(...),
    user_id: str = Header(None),
):
    """Upload audio file for transcription with subscription limits."""
    if not stt_service.is_available():
        raise HTTPException(status_code=503, detail="STT not available")

    final_user_id = user_id or "demo"
    
    audio_bytes = await audio.read()
    estimated_seconds = estimate_audio_duration(audio_bytes)
    
    # Check subscription
    can_stt, reason = subscription_manager.can_use_stt(final_user_id, estimated_seconds)
    if not can_stt:
        raise HTTPException(status_code=429, detail=reason)
    
    suffix = Path(audio.filename or "").suffix.lower() if audio.filename else ".webm"
    result = await stt_service.transcribe_audio(audio_bytes=audio_bytes, file_suffix=suffix or ".webm")
    
    # Track usage
    subscription_manager.add_stt_usage(final_user_id, estimated_seconds)
    stats = subscription_manager.get_usage_stats(final_user_id)
    
    result["metadata"] = {
        "stt_seconds_used": estimated_seconds,
        "stt_remaining_seconds": stats["stt_remaining_seconds"],
        "session_time_remaining": stats["session_time_remaining"],
    }
    
    return STTResponse(**result)


@router.post("/v1/stt", response_model=STTResponse)
async def stt_api(
    audio: UploadFile = File(...),
    user_id: str = Header(None),
):
    """Developer API: speech-to-text."""
    return await stt_upload(audio, user_id)


@router.get("/api/stt/info")
async def stt_info():
    """Get STT service info."""
    return stt_service.get_info()
