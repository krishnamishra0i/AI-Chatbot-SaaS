"""
Speech-to-Speech Real-time Endpoint
This endpoint handles the complete speech-to-speech pipeline:
1. Take audio input (from user's microphone)
2. Transcribe using Whisper (STT)
3. Send text to LLM for response
4. Generate speech response using TTS
5. Return audio response
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import asyncio
import concurrent.futures
from backend.utils.logger import setup_logger
from fastapi import BackgroundTasks

logger = setup_logger(__name__)

router = APIRouter()

# Module instances
stt_instance = None
llm_instance = None
tts_instance = None

# Streaming state
streaming_buffer = []
streaming_active = False
streaming_task = None
streaming_partial_response = ""
streaming_audio_chunks = []
streaming_tts_task = None


class SpeechToSpeechRequest(BaseModel):
    """Speech-to-speech request"""
    language: str = "en"
    voice: str = "en-US-GuyNeural"
    fast_mode: bool = False


class SpeechToSpeechResponse(BaseModel):
    """Speech-to-speech response"""
    success: bool
    transcribed_text: str
    response_text: str
    message: str


def set_stt_module(stt):
    """Set STT instance"""
    global stt_instance
    stt_instance = stt


def set_llm_module(llm):
    """Set LLM instance"""
    global llm_instance
    llm_instance = llm


def set_tts_module(tts):
    """Set TTS instance"""
    global tts_instance
    tts_instance = tts


async def start_llm_pre_generation(partial_text: str, fast_mode: bool = False):
    """Start LLM inference early with partial transcript"""
    global streaming_partial_response, streaming_task
    if streaming_task or not partial_text.strip():
        return
    loop = asyncio.get_event_loop()
    streaming_task = loop.run_in_executor(
        None,
        lambda: llm_instance.generate(partial_text.strip())
    )
    logger.info(f"Started LLM pre-generation with partial: '{partial_text.strip()}' (fast_mode={fast_mode})")


async def get_llm_response(voice: str = "en-US-GuyNeural"):
    """Get the LLM response if ready and start TTS immediately"""
    global streaming_partial_response, streaming_task, streaming_tts_task
    if not streaming_task:
        return None
    try:
        response = await streaming_task
        streaming_partial_response = response.get('response', '').strip()
        streaming_task = None
        
        # Start TTS immediately with partial response if fast_mode
        if streaming_partial_response and streaming_tts_task is None:
            await start_tts_streaming(streaming_partial_response, voice)
        
        return streaming_partial_response
    except Exception as e:
        logger.error(f"LLM pre-generation error: {e}")
        streaming_task = None
        return None


async def start_tts_streaming(text: str, voice: str):
    """Start TTS synthesis as soon as we have partial text"""
    global streaming_tts_task, streaming_audio_chunks
    if streaming_tts_task or not text.strip():
        return
    loop = asyncio.get_event_loop()
    streaming_tts_task = loop.run_in_executor(
        None,
        lambda: tts_instance.synthesize(text.strip(), voice)
    )
    logger.info(f"Started TTS streaming with partial: '{text.strip()}'")


async def get_tts_audio():
    """Get TTS audio if ready"""
    global streaming_audio_chunks, streaming_tts_task
    if not streaming_tts_task:
        return None
    try:
        audio = await streaming_tts_task
        streaming_audio_chunks.append(audio)
        streaming_tts_task = None
        return audio
    except Exception as e:
        logger.error(f"TTS streaming error: {e}")
        streaming_tts_task = None
        return None


@router.post("/speech-to-speech/process", response_class=StreamingResponse)
async def speech_to_speech_process(
    audio_file: UploadFile = File(...),
    language: str = "en",
    voice: str = "en-US-GuyNeural",
):
    """
    Complete speech-to-speech pipeline:
    1. Transcribe audio using Whisper STT
    2. Send text to LLM for response
    3. Convert response to speech using TTS
    4. Stream audio response back to client
    """
    try:
        if not stt_instance or not llm_instance or not tts_instance:
            raise HTTPException(
                status_code=503,
                detail="Speech-to-speech service not initialized. Required: STT, LLM, TTS"
            )

        # 1. Read audio file
        audio_bytes = await audio_file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="No audio data received")

        logger.info(f"📥 Received {len(audio_bytes)} bytes of audio")

        # 2. Transcribe audio using Whisper STT
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Convert audio bytes to array for Whisper
            import numpy as np
            import wave
            import io as io_module

            # Try to parse as WAV
            try:
                wav_file = wave.open(io_module.BytesIO(audio_bytes), 'rb')
                frames = wav_file.readframes(wav_file.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

                # Resample to 16kHz if needed
                original_rate = wav_file.getsampwidth()
                wav_file.close()
            except Exception as e:
                logger.warning(f"Could not parse WAV, trying raw audio: {e}")
                audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            # Transcribe with STT
            transcription_result = await loop.run_in_executor(
                executor,
                stt_instance.transcribe,
                audio_data,
                language
            )

        transcribed_text = transcription_result.get('text', '').strip()
        logger.info(f"✅ Transcribed: {transcribed_text}")

        if not transcribed_text:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")

        # 3. Get LLM response
        llm_response = await loop.run_in_executor(
            executor,
            llm_instance.generate,
            transcribed_text
        )
        response_text = llm_response.get('response', '').strip()
        logger.info(f"🤖 LLM Response: {response_text}")

        # 4. Convert response to speech using TTS
        audio_response = await loop.run_in_executor(
            executor,
            tts_instance.synthesize,
            response_text,
            None,
            language,
            voice
        )

        if not audio_response:
            raise HTTPException(status_code=500, detail="TTS synthesis failed")

        logger.info(f"✅ Generated {len(audio_response)} bytes of speech response")

        # 5. Return audio stream
        return StreamingResponse(
            io.BytesIO(audio_response),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=response.mp3"}
        )

    except Exception as e:
        logger.error(f"❌ Speech-to-speech error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/speech-to-speech/metadata")
async def speech_to_speech_metadata(
    audio_file: UploadFile = File(...),
    language: str = "en",
):
    """
    Speech-to-speech with metadata response (for testing/debugging)
    Returns transcribed text and LLM response as JSON
    """
    try:
        if not stt_instance or not llm_instance:
            raise HTTPException(
                status_code=503,
                detail="STT and LLM services not initialized"
            )

        # Read audio file
        audio_bytes = await audio_file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="No audio data received")

        # Transcribe audio
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            import numpy as np
            import wave
            import io as io_module

            try:
                wav_file = wave.open(io_module.BytesIO(audio_bytes), 'rb')
                frames = wav_file.readframes(wav_file.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                wav_file.close()
            except:
                audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            transcription_result = await loop.run_in_executor(
                executor,
                stt_instance.transcribe,
                audio_data,
                language
            )

        transcribed_text = transcription_result.get('text', '').strip()

        # Get LLM response
        llm_response = await loop.run_in_executor(
            executor,
            llm_instance.generate,
            transcribed_text
        )
        response_text = llm_response.get('response', '').strip()

        return SpeechToSpeechResponse(
            success=True,
            transcribed_text=transcribed_text,
            response_text=response_text,
            message="Speech-to-speech processing complete"
        )

    except Exception as e:
        logger.error(f"Speech-to-speech metadata error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/speech-to-speech/stream-start")
async def stream_start(request: SpeechToSpeechRequest):
    """Initialize streaming session"""
    global streaming_active, streaming_buffer, streaming_task
    streaming_active = True
    streaming_buffer = []
    logger.info(f"Speech-to-speech streaming started (fast_mode={request.fast_mode})")
    return {"status": "streaming_started", "fast_mode": request.fast_mode}


@router.post("/speech-to-speech/stream-chunk")
async def stream_chunk(audio_file: UploadFile = File(...), language: str = "en", fast_mode: bool = False):
    """Process a streaming audio chunk for fast partial transcription"""
    global streaming_active, streaming_buffer
    if not streaming_active:
        return {"status": "not_streaming"}

    try:
        # Read audio chunk
        audio_data = await audio_file.read()
        
        # Quick transcription with Whisper
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            transcription_result = await loop.run_in_executor(
                executor,
                stt_instance.transcribe,
                audio_data,
                language
            )
        transcribed_text = transcription_result.get('text', '').strip()
        
        # Store partial transcript
        if transcribed_text:
            streaming_buffer.append(transcribed_text)
            logger.info(f"Streaming chunk transcribed (fast_mode={fast_mode}): {transcribed_text}")
            
            # Start LLM pre-generation if we have enough text and no task running
            combined = " ".join(streaming_buffer).strip()
            if len(combined.split()) >= 3 and fast_mode:
                await start_llm_pre_generation(combined, fast_mode)
            
            return {"status": "chunk_processed", "partial_text": transcribed_text}
        else:
            return {"status": "chunk_processed", "partial_text": ""}
    except Exception as e:
        logger.error(f"Stream chunk error: {e}")
        return {"status": "error", "detail": str(e)}


@router.post("/speech-to-speech/stream-end")
async def stream_end(background_tasks: BackgroundTasks, request: SpeechToSpeechRequest):
    """Finalize streaming: generate full response and audio"""
    global streaming_active, streaming_buffer, streaming_partial_response, streaming_task, streaming_audio_chunks, streaming_tts_task
    streaming_active = False
    
    # Combine all partial transcripts
    full_transcript = " ".join(streaming_buffer).strip()
    streaming_buffer = []
    
    if not full_transcript:
        raise HTTPException(status_code=400, detail="No speech detected")
    
    try:
        # Try to get pre-generated LLM response
        response_text = streaming_partial_response
        if not response_text:
            # Check if LLM task is still running
            pre_generated = await get_llm_response(request.voice)
            if pre_generated:
                response_text = pre_generated
            else:
                # Generate normally
                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    llm_response = await loop.run_in_executor(
                        executor,
                        llm_instance.generate,
                        full_transcript
                    )
                    response_text = llm_response.get('response', '').strip()
        
        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to generate response")
        
        # Try to get pre-generated TTS audio
        tts_audio = await get_tts_audio()
        if not tts_audio:
            # Generate TTS normally
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                tts_audio = await loop.run_in_executor(
                    executor,
                    tts_instance.synthesize,
                    response_text,
                    request.voice
                )
        
        # Return streaming audio response
        def iter_audio():
            yield tts_audio
        
        background_tasks.add_task(lambda: logger.info(f"Stream end (fast_mode={request.fast_mode}): transcript='{full_transcript}', response='{response_text}'"))
        
        return StreamingResponse(
            iter_audio(),
            media_type="audio/mpeg",
            headers={
                "X-Transcript": full_transcript,
                "X-Response": response_text,
                "X-Fast-Mode": str(request.fast_mode),
                "X-Instant-TTS": str(tts_audio is not None)
            }
        )
    except Exception as e:
        logger.error(f"Stream end error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Reset streaming state
        streaming_partial_response = ""
        streaming_task = None
        streaming_audio_chunks = []
        streaming_tts_task = None
