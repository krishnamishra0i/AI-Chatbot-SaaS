"""
Enhanced Chat Routes with Voice & Avatar Integration
Supports: Text-Chat, Voice-Input (STT), Voice-Output (TTS), Avatar Video (D-ID)
"""

import json
import os
import asyncio
import io
import base64
from datetime import datetime
from typing import Optional, Dict, List
from fastapi import APIRouter, HTTPException, File, UploadFile, WebSocket, Query
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Models
class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "en"
    use_voice: Optional[bool] = True
    voice_type: Optional[str] = "natural"  # natural, professional, casual

class ChatResponse(BaseModel):
    response: str
    confidence: float = 0.95
    sources: Optional[List[str]] = None
    timestamp: Optional[str] = None
    audio_url: Optional[str] = None
    avatar_video: Optional[str] = None

class TranscriptionRequest(BaseModel):
    audio: str  # base64 encoded audio
    language: Optional[str] = "en"

class TranscriptionResponse(BaseModel):
    transcription: str
    confidence: float
    language: str

# Router Setup
router = APIRouter(prefix="/api", tags=["chat"])

# Global instances (initialized in main)
llm = None
retriever = None
tts = None
asr = None
d_id_client = None
kb_loaded = False

def initialize_routes(llm_instance, retriever_instance, tts_instance, asr_instance, d_id_instance=None, kb_status=False):
    """Initialize route dependencies"""
    global llm, retriever, tts, asr, d_id_client, kb_loaded
    llm = llm_instance
    retriever = retriever_instance
    tts = tts_instance
    asr = asr_instance
    d_id_client = d_id_instance
    kb_loaded = kb_status


# ============= MAIN CHAT ENDPOINT (TEXT & VOICE) =============
@router.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """
    Main chat endpoint supporting:
    - Text-only chat
    - Voice input with automatic transcription
    - Voice output with TTS generation
    - Knowledge base retrieval
    - Avatar video generation (D-ID)
    """
    try:
        if not llm:
            raise HTTPException(status_code=503, detail="LLM not initialized")

        message = request.message.strip()
        if not message:
            raise HTTPException(status_code=400, detail="Empty message")

        # Step 1: Retrieve context from knowledge base if available
        sources = []
        context = ""
        if kb_loaded and retriever:
            try:
                retrieved = retriever.retrieve(message, k=3)
                context = "\n".join([doc.get('content', '') for doc in retrieved])
                sources = [doc.get('source', 'Knowledge Base') for doc in retrieved]
            except Exception as e:
                logger.warning(f"KB retrieval failed: {e}")

        # Step 2: Generate response with LLM
        try:
            system_prompt = f"""You are a professional AI Assistant integrated with an avatar system. 
Respond naturally and conversationally. Keep responses concise (2-3 sentences).

{('Knowledge Base Context:\n' + context) if context else ''}"""

            # Use synchronous generate method (LLM handles async internally)
            response_text = llm.generate(
                prompt=message,
                system_prompt=system_prompt,
                max_tokens=500,
                temperature=0.7
            )
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            response_text = "I apologize, but I encountered an issue generating a response. Please try again."

        # Step 3: Generate voice response if requested
        audio_url = None
        voice_type = request.voice_type or "natural"
        if request.use_voice and tts:
            try:
                audio_data = await generate_voice_response(response_text, voice_type)
                if audio_data:
                    audio_url = f"data:audio/wav;base64,{audio_data}"
            except Exception as e:
                logger.warning(f"TTS generation failed: {e}")

        # Step 4: Generate avatar video if D-ID available
        avatar_video = None
        if d_id_client:
            try:
                avatar_video = await generate_avatar_video(response_text, voice_type)
            except Exception as e:
                logger.warning(f"Avatar generation failed: {e}")

        return ChatResponse(
            response=response_text,
            confidence=0.95 if kb_loaded else 0.85,
            sources=sources if sources else None,
            timestamp=datetime.now().isoformat(),
            audio_url=audio_url,
            avatar_video=avatar_video
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


# ============= VOICE/AUDIO ENDPOINTS =============

@router.post("/transcribe-audio")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio file to text using Whisper ASR
    Supports: WAV, MP3, OGG, FLAC, M4A
    """
    try:
        if not asr:
            raise HTTPException(status_code=503, detail="Speech-to-Text not available")

        # Read audio file
        audio_data = await file.read()
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")

        # Transcribe
        transcription = await asr.transcribe_async(audio_data)
        
        if not transcription:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")

        return {
            "transcription": transcription.get("text", ""),
            "confidence": transcription.get("confidence", 0.0),
            "language": transcription.get("language", "en"),
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/generate-speech")
async def generate_speech(request: Dict):
    """
    Generate speech audio from text using TTS
    Returns: Audio file as base64 or direct play URL
    """
    try:
        if not tts:
            raise HTTPException(status_code=503, detail="Text-to-Speech not available")

        text = request.get("text", "").strip()
        voice_type = request.get("voice_type", "natural")
        language = request.get("language", "en")

        if not text:
            raise HTTPException(status_code=400, detail="Empty text")

        audio_data = await generate_voice_response(text, voice_type, language)
        
        return {
            "audio": audio_data,
            "format": "wav",
            "duration_estimate": f"{len(text.split()) * 0.5:.1f}s",
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech generation failed: {str(e)}")


# ============= AVATAR/VIDEO ENDPOINTS =============

@router.post("/generate-avatar-video")
async def generate_avatar_video_endpoint(request: Dict):
    """
    Generate avatar video response using D-ID API
    Returns: Video URL for streaming
    """
    try:
        if not d_id_client:
            raise HTTPException(status_code=503, detail="Avatar service not available")

        text = request.get("text", "").strip()
        voice = request.get("voice", "en-US-AriaNeural")

        if not text:
            raise HTTPException(status_code=400, detail="Empty text")

        video_url = await generate_avatar_video(text, voice)
        
        return {
            "video_url": video_url,
            "provider": "D-ID",
            "format": "mp4",
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Avatar generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Avatar generation failed: {str(e)}")


# ============= STREAMING ENDPOINT =============

@router.websocket("/chat/stream")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time streaming chat
    Allows for immediate response streaming without waiting for full completion
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "").strip()

            if not message:
                await websocket.send_json({"error": "Empty message"})
                continue

            # Stream response
            try:
                if llm:
                    async for chunk in llm.stream_async(message):
                        await websocket.send_text(chunk)
                else:
                    await websocket.send_json({"error": "LLM not available"})
            except Exception as e:
                logger.error(f"Stream error: {e}")
                await websocket.send_json({"error": str(e)})

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()


# ============= KNOWLEDGE BASE ENDPOINTS =============

@router.get("/knowledge-base/stats")
async def get_kb_stats():
    """Get knowledge base statistics"""
    try:
        if not retriever:
            return {
                "status": "not_loaded",
                "total_documents": 0,
                "indexed": False
            }

        stats = retriever.get_stats() if hasattr(retriever, 'get_stats') else {}
        
        return {
            "status": "loaded" if kb_loaded else "available",
            "total_documents": stats.get("total_documents", 0),
            "indexed": kb_loaded,
            "last_updated": stats.get("last_updated", "Unknown"),
            "size_mb": stats.get("size_mb", 0)
        }

    except Exception as e:
        logger.error(f"KB stats error: {e}")
        return {"status": "error", "error": str(e)}


@router.post("/knowledge-base/reload")
async def reload_knowledge_base():
    """Reload knowledge base from disk"""
    try:
        global kb_loaded
        if not retriever:
            raise HTTPException(status_code=503, detail="Retriever not available")

        if hasattr(retriever, 'reload'):
            await retriever.reload()
        
        kb_loaded = True
        
        return {
            "status": "success",
            "message": "Knowledge base reloaded",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"KB reload error: {e}")
        raise HTTPException(status_code=500, detail=f"KB reload failed: {str(e)}")


# ============= HEALTH ENDPOINTS =============

@router.get("/health")
async def health_check():
    """System health status"""
    return {
        "status": "healthy",
        "llm": "active" if llm else "inactive",
        "tts": "active" if tts else "inactive",
        "asr": "active" if asr else "inactive",
        "avatar": "active" if d_id_client else "inactive",
        "knowledge_base": "loaded" if kb_loaded else "not_loaded",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/system-info")
async def system_info():
    """System information and configuration"""
    return {
        "server": "Premium AI Avatar Chatbot",
        "version": "2.0",
        "features": {
            "text_chat": True,
            "voice_input": bool(asr),
            "voice_output": bool(tts),
            "avatar_video": bool(d_id_client),
            "knowledge_base": bool(retriever),
            "streaming": True,
            "websocket": True
        },
        "max_message_length": 2000,
        "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko"],
        "models": {
            "llm": "Groq LLaMA",
            "tts": "ModernTTS / EdgeTTS",
            "asr": "Whisper",
            "avatar": "D-ID"
        }
    }


# ============= HELPER FUNCTIONS =============

async def generate_voice_response(text: str, voice_type: str = "natural", language: str = "en") -> Optional[str]:
    """Generate audio response from text"""
    try:
        if not tts:
            return None

        # Generate audio based on available TTS
        if hasattr(tts, 'generate_audio_async'):
            audio_bytes = await tts.generate_audio_async(text, voice_type, language)
        elif hasattr(tts, 'generate_audio'):
            audio_bytes = tts.generate_audio(text, voice_type, language)
        else:
            return None

        # Convert to base64 if bytes
        if isinstance(audio_bytes, bytes):
            return base64.b64encode(audio_bytes).decode('utf-8')
        return audio_bytes

    except Exception as e:
        logger.error(f"Voice generation error: {e}")
        return None


async def generate_avatar_video(text: str, voice: str = "en-US-AriaNeural") -> Optional[str]:
    """Generate avatar video using D-ID API"""
    try:
        if not d_id_client:
            return None

        # Call D-ID API
        if hasattr(d_id_client, 'create_video_async'):
            video_data = await d_id_client.create_video_async(text, voice)
        elif hasattr(d_id_client, 'create_video'):
            video_data = d_id_client.create_video(text, voice)
        else:
            return None

        return video_data.get('video_url') if isinstance(video_data, dict) else video_data

    except Exception as e:
        logger.error(f"Avatar generation error: {e}")
        return None


def format_markdown(text: str) -> str:
    """Convert markdown to HTML"""
    import re
    
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Code
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    # Line breaks
    text = text.replace('\n', '<br>')
    
    return text
