"""
Advanced TTS/STT API routes
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import io
import asyncio
import numpy as np
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

# Store module instances
tts_instance = None
stt_instance = None
voice_trainer = None


class TTSRequest(BaseModel):
    """TTS synthesis request"""
    text: str
    language: str = "en"
    speaker_name: Optional[str] = None
    voice: Optional[str] = None  # e.g., 'en-US-GuyNeural' for male voice


class TTSResponse(BaseModel):
    """TTS response"""
    success: bool
    message: str
    duration: Optional[float] = None


class STTRequest(BaseModel):
    """STT transcription request"""
    language: Optional[str] = None


class STTResponse(BaseModel):
    """STT response"""
    text: str
    language: str
    confidence: float


class VoiceTrainRequest(BaseModel):
    """Voice training request"""
    speaker_name: str
    num_epochs: int = 10
    learning_rate: float = 1e-4


class VoiceTrainResponse(BaseModel):
    """Voice training response"""
    success: bool
    speaker_name: str
    message: str


def set_tts_module(tts):
    """Set TTS instance"""
    global tts_instance
    tts_instance = tts


def set_stt_module(stt):
    """Set STT instance"""
    global stt_instance
    stt_instance = stt


def set_voice_trainer(trainer):
    """Set voice trainer instance"""
    global voice_trainer
    voice_trainer = trainer


# ==================== TTS Endpoints ====================

@router.post("/tts/synthesize-audio", response_class=StreamingResponse)
async def synthesize_audio_bytes(request: TTSRequest):
    """
    Synthesize text to speech and return audio bytes
    Returns: MP3 audio bytes that can be played directly in HTML audio element
    """
    try:
        if not tts_instance:
            raise HTTPException(status_code=503, detail="TTS not initialized")
        
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        import concurrent.futures
        from fastapi.responses import StreamingResponse
        
        # Run TTS in thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # synthesize(text, speaker_wav:Optional[str]=None, language:str='en', voice:Optional[str]=None)
            audio_bytes = await loop.run_in_executor(
                executor,
                tts_instance.synthesize,
                request.text,
                None,
                request.language,
                request.voice
            )
        
        if audio_bytes is None or len(audio_bytes) == 0:
            raise HTTPException(status_code=500, detail="TTS synthesis failed - no audio generated")
        
        logger.info(f"✅ Generated {len(audio_bytes)} bytes of audio")
        
        # Return as MP3 audio stream
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=speech.mp3"}
        )
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts/synthesize", response_model=TTSResponse)
async def synthesize_tts(request: TTSRequest):
    """Synthesize text to speech (metadata only - use /tts/synthesize-audio for audio bytes)"""
    try:
        if not tts_instance:
            raise HTTPException(status_code=503, detail="TTS not initialized")
        
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        import concurrent.futures
        
        # Run TTS in thread pool
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            audio_bytes = await loop.run_in_executor(
                executor,
                tts_instance.synthesize,
                request.text,
                None,
                request.language
            )
        
        if audio_bytes is None:
            raise HTTPException(status_code=500, detail="TTS synthesis failed")
        
        # Estimate duration (MP3 average bitrate ~128 kbps)
        duration = (len(audio_bytes) * 8) / (128 * 1000)
        
        return TTSResponse(
            success=True,
            message=f"TTS synthesis successful ({len(audio_bytes)} bytes)",
            duration=duration
        )
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts/synthesize-file")
async def synthesize_to_file(
    text: str = Form(...),
    filename: str = Form(default="output.mp3"),
    language: str = Form(default="en"),
    speaker_name: Optional[str] = Form(None)
):
    """Synthesize TTS and return audio file"""
    try:
        if not tts_instance:
            raise HTTPException(status_code=503, detail="TTS not initialized")
        
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        from fastapi.responses import StreamingResponse
        import concurrent.futures
        
        # Run TTS in thread pool
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            audio_bytes = await loop.run_in_executor(
                executor,
                tts_instance.synthesize,
                text,
                None,
                language
            )
        
        if audio_bytes is None or len(audio_bytes) == 0:
            raise HTTPException(status_code=500, detail="Synthesis failed - no audio generated")
        
        logger.info(f"✅ Generated {len(audio_bytes)} bytes of audio")
        
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"TTS file synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STT Endpoints ====================

@router.post("/stt/transcribe", response_model=STTResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(None),
    language: Optional[str] = None
):
    """Transcribe audio file to text"""
    try:
        if not stt_instance:
            raise HTTPException(status_code=503, detail="STT not initialized")
        
        # Check if file was provided
        if audio_file is None or audio_file.size == 0:
            return STTResponse(
                text="",
                language=language or "en",
                confidence=0.0
            )
        
        # Read audio file
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            return STTResponse(
                text="",
                language=language or "en",
                confidence=0.0
            )
        
        # Try to transcribe
        try:
            import librosa
            # Load audio from bytes
            audio, sr = librosa.load(io.BytesIO(audio_data), sr=16000, mono=True)
        except Exception as e_librosa:
            logger.warning(f"Librosa failed to load audio: {e_librosa}. Trying numpy fallback...")
            try:
                # Fallback: try to use numpy directly for common formats
                import numpy as np
                audio = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            except Exception as e_numpy:
                logger.error(f"Audio loading failed: {e_librosa}, {e_numpy}")
                return STTResponse(
                    text="",
                    language=language or "en",
                    confidence=0.0
                )
        
        # Transcribe using Whisper
        result = stt_instance.transcribe(audio, language=language)
        
        return STTResponse(
            text=result.get("text", "").strip(),
            language=result.get("language", language or "en"),
            confidence=result.get("confidence", 0.0)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STT error: {e}", exc_info=True)
        # Return empty response instead of error to avoid 500
        return STTResponse(
            text="",
            language=language or "en",
            confidence=0.0
        )


@router.post("/stt/transcribe-base64", response_model=STTResponse)
async def transcribe_base64(
    audio_base64: str = Form(None),
    audio_binary: bytes = Form(None),
    language: Optional[str] = None
):
    """Transcribe audio from base64 or binary data (for browser MediaRecorder)"""
    try:
        if not stt_instance:
            raise HTTPException(status_code=503, detail="STT not initialized")
        
        # Get audio data from base64 or binary
        audio_data = None
        if audio_base64:
            import base64
            try:
                audio_data = base64.b64decode(audio_base64)
            except Exception as e:
                logger.error(f"Base64 decode error: {e}")
                return STTResponse(text="", language=language or "en", confidence=0.0)
        elif audio_binary:
            audio_data = audio_binary
        else:
            return STTResponse(text="", language=language or "en", confidence=0.0)
        
        if not audio_data or len(audio_data) == 0:
            return STTResponse(text="", language=language or "en", confidence=0.0)
        
        # Try to load and transcribe
        try:
            import librosa
            audio, sr = librosa.load(io.BytesIO(audio_data), sr=16000, mono=True)
        except Exception as e_librosa:
            logger.warning(f"Librosa failed: {e_librosa}. Trying raw audio...")
            try:
                import numpy as np
                # Try as raw PCM data
                audio = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            except Exception as e_np:
                logger.error(f"Audio loading failed: {e_librosa}, {e_np}")
                return STTResponse(text="", language=language or "en", confidence=0.0)
        
        # Transcribe
        result = stt_instance.transcribe(audio, language=language)
        
        return STTResponse(
            text=result.get("text", "").strip(),
            language=result.get("language", language or "en"),
            confidence=result.get("confidence", 0.0)
        )
    except Exception as e:
        logger.error(f"Base64 transcription error: {e}", exc_info=True)
        return STTResponse(text="", language=language or "en", confidence=0.0)


# ==================== Voice Training Endpoints ====================

@router.post("/training/prepare-data")
async def prepare_training_data(
    voice_sample_dir: str = Form(...),
    language: str = Form(default="en")
):
    """Prepare training data from voice samples"""
    try:
        if not voice_trainer:
            raise HTTPException(status_code=503, detail="Voice trainer not initialized")
        
        metadata = voice_trainer.prepare_training_data(
            voice_sample_dir=voice_sample_dir,
            language=language
        )
        
        return {
            "success": "error" not in metadata,
            "metadata": metadata
        }
    except Exception as e:
        logger.error(f"Data preparation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/training/fine-tune", response_model=VoiceTrainResponse)
async def fine_tune_voice(request: VoiceTrainRequest):
    """Start fine-tuning a custom voice"""
    try:
        if not voice_trainer:
            raise HTTPException(status_code=503, detail="Voice trainer not initialized")
        
        # Create training data directory if provided
        training_dir = f"data/training_voices/{request.speaker_name}"
        
        result = voice_trainer.fine_tune(
            training_data_dir=training_dir,
            speaker_name=request.speaker_name,
            num_epochs=request.num_epochs,
            learning_rate=request.learning_rate
        )
        
        if "error" in result:
            return VoiceTrainResponse(
                success=False,
                speaker_name=request.speaker_name,
                message=result.get("error", "Training failed")
            )
        
        return VoiceTrainResponse(
            success=True,
            speaker_name=request.speaker_name,
            message=f"Voice '{request.speaker_name}' trained successfully"
        )
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training/speakers")
async def list_trained_speakers():
    """List all trained speakers"""
    try:
        if not voice_trainer:
            return {"speakers": []}
        
        speakers = voice_trainer.list_trained_speakers()
        
        return {
            "success": True,
            "count": len(speakers),
            "speakers": speakers
        }
    except Exception as e:
        logger.error(f"Error listing speakers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training/speaker/{speaker_name}")
async def get_speaker_info(speaker_name: str):
    """Get information about a trained speaker"""
    try:
        if not voice_trainer:
            raise HTTPException(status_code=404, detail="Speaker not found")
        
        info = voice_trainer.get_speaker_info(speaker_name)
        
        if info is None:
            raise HTTPException(status_code=404, detail=f"Speaker '{speaker_name}' not found")
        
        return {
            "success": True,
            "speaker_name": speaker_name,
            "info": info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting speaker info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/training/speaker/{speaker_name}")
async def delete_speaker(speaker_name: str):
    """Delete a trained speaker"""
    try:
        if not voice_trainer:
            raise HTTPException(status_code=503, detail="Voice trainer not initialized")
        
        success = voice_trainer.delete_trained_speaker(speaker_name)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Speaker '{speaker_name}' not found")
        
        return {
            "success": True,
            "message": f"Speaker '{speaker_name}' deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting speaker: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts/with-trained-voice")
async def synthesize_with_trained_voice(
    text: str = Form(...),
    speaker_name: str = Form(...),
    language: str = Form(default="en")
):
    """Synthesize using a trained custom voice"""
    try:
        if not voice_trainer:
            raise HTTPException(status_code=503, detail="Voice trainer not initialized")
        
        audio = voice_trainer.synthesize_with_trained_voice(
            text=text,
            speaker_name=speaker_name,
            language=language
        )
        
        if audio is None:
            raise HTTPException(status_code=500, detail="Synthesis with trained voice failed")
        
        # Return duration info
        duration = len(audio) / 24000.0
        
        return {
            "success": True,
            "speaker": speaker_name,
            "duration": duration,
            "message": f"Synthesized {duration:.2f}s of speech"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error synthesizing with trained voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))
