"""
WebSocket routes for real-time audio and text
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.utils.logger import setup_logger
import json

logger = setup_logger(__name__)

router = APIRouter()

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove connection"""
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Send message to all clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")

manager = ConnectionManager()

# Store for modules
asr_instance = None
tts_instance = None
llm_instance = None
rag_retriever = None

def set_modules(asr, tts, llm, rag):
    """Set module instances"""
    global asr_instance, tts_instance, llm_instance, rag_retriever
    asr_instance = asr
    tts_instance = tts
    llm_instance = llm
    rag_retriever = rag

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            message_type = data.get("type", "text")
            
            if message_type == "text":
                # Handle text message
                user_text = data.get("message", "")
                
                if llm_instance:
                    # Get RAG context
                    context = None
                    if rag_retriever:
                        context = rag_retriever.get_context(user_text, top_k=3)
                    
                    # Generate response
                    response = llm_instance.generate(user_text, context)
                    
                    # Send response
                    await websocket.send_json({
                        "type": "text",
                        "message": response,
                        "user_input": user_text
                    })
                    
                    # If TTS available, generate audio
                    if tts_instance:
                        try:
                            audio = tts_instance.synthesize(response)
                            if audio is not None:
                                await websocket.send_json({
                                    "type": "audio",
                                    "audio_data": audio.tolist()
                                })
                        except Exception as e:
                            logger.error(f"TTS error: {e}")
            
            elif message_type == "audio":
                # Handle audio message (speech-to-text)
                audio_data = data.get("audio_data", [])
                
                if asr_instance and audio_data:
                    try:
                        import numpy as np
                        audio_array = np.array(audio_data, dtype=np.float32)
                        result = asr_instance.transcribe(audio_array)
                        
                        await websocket.send_json({
                            "type": "transcription",
                            "text": result.get("text", ""),
                            "language": result.get("language", "en")
                        })
                    except Exception as e:
                        logger.error(f"ASR error: {e}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
