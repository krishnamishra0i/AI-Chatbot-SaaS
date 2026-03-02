"""
STT routes — speech-to-text transcription.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from pydantic import BaseModel
from typing import Optional

from api.schemas.schemas import STTResponse
from api.services import stt_service

router = APIRouter(tags=["Speech-to-Text"])


class STTBase64Request(BaseModel):
    audio: str  # base64-encoded audio


@router.post("/api/stt", response_model=STTResponse)
async def speech_to_text(file: Optional[UploadFile] = File(None)):
    """
    Convert speech to text via file upload (multipart).
    """
    if not stt_service.is_available():
        raise HTTPException(status_code=503, detail="STT not available. Install openai-whisper.")

    if not file:
        raise HTTPException(status_code=400, detail="Provide audio file")

    audio_bytes = await file.read()
    result = await stt_service.transcribe_audio(audio_bytes=audio_bytes)
    return STTResponse(**result)


@router.post("/api/stt/base64", response_model=STTResponse)
async def speech_to_text_base64(body: STTBase64Request):
    """Convert speech to text via base64 JSON body."""
    if not stt_service.is_available():
        raise HTTPException(status_code=503, detail="STT not available. Install openai-whisper.")

    result = await stt_service.transcribe_audio(audio_base64=body.audio)
    return STTResponse(**result)


@router.post("/api/stt/upload", response_model=STTResponse)
async def stt_upload(audio: UploadFile = File(...)):
    """Upload audio file for transcription."""
    if not stt_service.is_available():
        raise HTTPException(status_code=503, detail="STT not available")

    audio_bytes = await audio.read()
    result = await stt_service.transcribe_audio(audio_bytes=audio_bytes)
    return STTResponse(**result)


@router.post("/v1/stt", response_model=STTResponse)
async def stt_api(audio: UploadFile = File(...)):
    """Developer API: speech-to-text."""
    return await stt_upload(audio)


@router.get("/api/stt/info")
async def stt_info():
    """Get STT service info."""
    return stt_service.get_info()
