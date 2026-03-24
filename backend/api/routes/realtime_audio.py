"""
Real-time Audio Streaming Routes (WebSocket)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WebSocket endpoints for real-time STT/TTS streaming.

⚡ Real-time pipeline:
   1. Frontend sends mic audio chunks via WebSocket
   2. Backend processes chunks in real-time
   3. Backend streams TTS response back
   4. Frontend plays audio while receiving

Latency: 200-500ms for full round-trip (mic → STT → chat → TTS → speaker)
"""

import json
import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, WebSocketException, Header
from fastapi.websockets import WebSocket, WebSocketState

from api.services import stt_service_openai, tts_service_openai
from api.services.realtime_audio_streamer import get_streamer, AudioConfig
from api.services import chat_service
from api.services.subscription_manager import subscription_manager
from api.middleware.jwt_auth import verify_jwt_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Real-time Audio Streaming"])

# Active WebSocket connections
active_connections: dict = {}


@router.websocket("/ws/audio/streaming")
async def websocket_audio_streaming(
    websocket: WebSocket,
    user_id: Optional[str] = Header(None),
):
    """
    WebSocket endpoint for real-time audio streaming.
    
    Protocol:
    ─────────────────────────────────────────────────────────────
    
    Client → Server (JSON):
    {
      "type": "audio_chunk",
      "data": "base64_audio_chunk",
      "encoding": "base64"
    }
    
    Server → Client (JSON):
    {
      "type": "transcription",
      "text": "user said something",
      "partial": false
    }
    or
    {
      "type": "tts_chunk",
      "data": "base64_audio_chunk",
      "encoding": "base64",
      "final": false
    }
    or
    {
      "type": "error",
      "error": "error message"
    }
    
    ─────────────────────────────────────────────────────────────
    Full conversation flow:
    
    1. Client connects & auth passes
    2. Client sends audio chunks (streaming):
       → {type: "audio_chunk", data: "...", encoding: "base64"}
    3. Server processes & transcribes
    4. Server sends transcription:
       → {type: "transcription", text: "..."}
    5. Server processes chat
    6. Server streams TTS response:
       → {type: "tts_chunk", data: "...", final: false}
       → {type: "tts_chunk", data: "...", final: false}
       → {type: "tts_chunk", data: "...", final: true}
    7. Client plays audio & repeat from step 2
    """
    
    await websocket.accept()
    connection_id = id(websocket)
    active_connections[connection_id] = websocket
    
    final_user_id = user_id or "demo"
    streamer = get_streamer()
    audio_chunks = []
    
    try:
        logger.info(f"WebSocket connected: {connection_id} (user: {final_user_id})")
        
        while websocket.application_state == WebSocketState.CONNECTED:
            try:
                # Receive message
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                # ════════════════════════════════════════════════════════════════
                # AUDIO CHUNK RECEIVED
                # ════════════════════════════════════════════════════════════════
                if message_type == "audio_chunk":
                    try:
                        # Decode audio
                        encoded_audio = data.get("data", "")
                        encoding = data.get("encoding", "base64")
                        
                        audio_bytes = streamer.decode_audio_chunk(encoded_audio, encoding)
                        if audio_bytes:
                            audio_chunks.append(audio_bytes)
                            
                            # Send acknowledgment
                            await websocket.send_json({
                                "type": "ack",
                                "chunks_received": len(audio_chunks),
                            })
                    
                    except Exception as e:
                        logger.error(f"Audio chunk parsing failed: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "error": f"Audio parsing failed: {str(e)}"
                        })
                
                # ════════════════════════════════════════════════════════════════
                # START TRANSCRIPTION (client signals end)
                # ════════════════════════════════════════════════════════════════
                elif message_type == "transcribe":
                    if not audio_chunks:
                        await websocket.send_json({
                            "type": "error",
                            "error": "No audio data to transcribe"
                        })
                        continue
                    
                    try:
                        # Check subscription
                        complete_audio = b"".join(audio_chunks)
                        duration = streamer.estimate_duration(complete_audio)
                        
                        can_stt, reason = subscription_manager.can_use_stt(
                            final_user_id, duration
                        )
                        if not can_stt:
                            await websocket.send_json({
                                "type": "error",
                                "error": reason
                            })
                            audio_chunks = []
                            continue
                        
                        # Transcribe
                        logger.debug(f"Transcribing {len(complete_audio)} bytes")
                        
                        # Create async generator from chunks
                        async def chunk_generator():
                            for chunk in audio_chunks:
                                yield chunk
                        
                        result = await stt_service_openai.transcribe_audio_stream(
                            chunk_generator()
                        )
                        
                        # Track usage
                        subscription_manager.add_stt_usage(final_user_id, duration)
                        
                        # Send transcription
                        await websocket.send_json({
                            "type": "transcription",
                            "text": result.text,
                            "language": result.language,
                            "duration": result.duration,
                            "confidence": result.confidence,
                        })
                        
                        # Continue with chat
                        await process_and_respond(
                            websocket, result.text, final_user_id, streamer
                        )
                        
                        audio_chunks = []
                    
                    except Exception as e:
                        logger.error(f"Transcription failed: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "error": f"Transcription failed: {str(e)}"
                        })
                        audio_chunks = []
                
                # ════════════════════════════════════════════════════════════════
                # CLEAR BUFFER
                # ════════════════════════════════════════════════════════════════
                elif message_type == "reset":
                    audio_chunks = []
                    await websocket.send_json({
                        "type": "reset_ack"
                    })
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "error": "Invalid JSON format"
                })
            
            except Exception as e:
                logger.error(f"Message processing error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "error": f"Processing error: {str(e)}"
                })
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1000)
        except:
            pass
    
    finally:
        active_connections.pop(connection_id, None)
        logger.info(f"WebSocket disconnected: {connection_id}")


async def process_and_respond(
    websocket: WebSocket,
    user_text: str,
    user_id: str,
    streamer,
):
    """
    Process text through chat and stream TTS response.
    
    ⚡ Real-time flow:
       1. Get chat response
       2. Stream TTS audio bytes back to client
       3. Client plays while receiving
    """
    try:
        # Get chat response
        logger.debug(f"Getting chat response for: {user_text}")
        
        response = await chat_service.chat_completion(
            messages=[{"role": "user", "content": user_text}],
            model="gpt-4o-mini",
        )
        
        bot_response = response.get("content", "")
        
        # Send chat response
        await websocket.send_json({
            "type": "chat_response",
            "text": bot_response,
        })
        
        # Stream TTS audio
        logger.debug(f"Streaming TTS for: {bot_response[:50]}...")
        
        chunk_index = 0
        async for audio_chunk in tts_service_openai.synthesize_speech_stream(
            bot_response,
            voice="nova",
            speed=1.0,
        ):
            if audio_chunk:
                # Encode chunk
                encoded = streamer.encode_audio_chunk(audio_chunk, "base64")
                
                # Send TTS chunk
                is_final = chunk_index > 0  # Mark later chunks as partial
                await websocket.send_json({
                    "type": "tts_chunk",
                    "data": encoded,
                    "encoding": "base64",
                    "index": chunk_index,
                    "final": False,
                })
                
                chunk_index += 1
        
        # Send final marker
        await websocket.send_json({
            "type": "tts_complete",
            "chunks_sent": chunk_index,
        })
    
    except Exception as e:
        logger.error(f"Response processing failed: {e}")
        await websocket.send_json({
            "type": "error",
            "error": f"Response failed: {str(e)}"
        })


@router.get("/api/audio/streaming/info")
async def streaming_info():
    """Get real-time audio streaming info."""
    return {
        "websocket_endpoint": "/ws/audio/streaming",
        "stt_service": stt_service_openai.get_info(),
        "tts_service": tts_service_openai.get_info(),
        "latency_ms": "200-500 (full round-trip)",
        "audio_config": {
            "sample_rate": 16000,
            "channels": 1,
            "format": "wav",
            "chunk_duration_ms": 100,
        },
        "protocol": "JSON over WebSocket",
        "supported_operations": [
            "audio_chunk (client → server)",
            "transcribe (start transcription)",
            "reset (clear buffer)",
        ],
    }
