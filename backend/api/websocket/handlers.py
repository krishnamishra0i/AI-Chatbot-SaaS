"""
WebSocket endpoints — real-time streaming chat, TTS, avatar frames.
Implements the full pipeline: User -> STT -> LLM -> TTS -> LipSync -> Avatar -> Browser
"""

import json
import asyncio
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set

from api.services import chat_service, tts_service, avatar_service
from api.services.memory_service import get_memory

router = APIRouter()
memory = get_memory()

# ---- Connection Manager ----

class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str = "default"):
        await websocket.accept()
        if room not in self.active:
            self.active[room] = set()
        self.active[room].add(websocket)

    def disconnect(self, websocket: WebSocket, room: str = "default"):
        if room in self.active:
            self.active[room].discard(websocket)
            if not self.active[room]:
                del self.active[room]

    async def send_json(self, websocket: WebSocket, data: dict):
        await websocket.send_json(data)

    async def broadcast(self, room: str, data: dict):
        if room in self.active:
            for ws in self.active[room]:
                try:
                    await ws.send_json(data)
                except Exception:
                    pass


manager = ConnectionManager()


# ---- Chat WebSocket (Streaming with Memory) ----

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    Real-time streaming chat via WebSocket with conversation memory.
    
    Client sends:
      {"message": "Hello", "session_id": "...", "model": "groq/llama-3.3-70b-versatile",
       "stream": true, "temperature": 0.7}
    
    Server sends:
      {"type": "start", "timestamp": ...}
      {"type": "chunk", "content": "..."}
      {"type": "sentence", "content": "..."}     (for TTS pipeline)
      {"type": "done", "content": "...", "latency_ms": ..., "provider": "..."}
    """
    await manager.connect(websocket, "chat")
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            message = data.get("message", "")
            session_id = data.get("session_id", "default")
            model = data.get("model", None)
            stream = data.get("stream", True)
            temperature = data.get("temperature", 0.7)

            # Build context with memory
            context_messages = memory.get_context_window(
                session_id=session_id,
                system_prompt="",
                user_message=message,
            )
            context_messages = [m for m in context_messages if m.get("content")]

            start_time = time.time()
            await manager.send_json(websocket, {
                "type": "start",
                "timestamp": start_time,
            })

            if stream:
                full_content = ""
                sentence_buffer = ""
                first_token = True

                async for chunk in chat_service.chat_completion_stream(
                    context_messages, model=model, temperature=temperature
                ):
                    if first_token:
                        first_token_ms = (time.time() - start_time) * 1000
                        await manager.send_json(websocket, {
                            "type": "first_token",
                            "latency_ms": round(first_token_ms, 1),
                        })
                        first_token = False

                    full_content += chunk
                    sentence_buffer += chunk

                    # Send raw token
                    await manager.send_json(websocket, {
                        "type": "chunk",
                        "content": chunk,
                    })

                    # Check for sentence boundaries (for TTS pipeline)
                    for sep in [". ", "! ", "? ", ".\n", "!\n", "?\n"]:
                        while sep in sentence_buffer:
                            idx = sentence_buffer.find(sep)
                            sentence = sentence_buffer[:idx + 1].strip()
                            sentence_buffer = sentence_buffer[idx + len(sep):]
                            if sentence:
                                await manager.send_json(websocket, {
                                    "type": "sentence",
                                    "content": sentence,
                                })

                # Flush remaining sentence buffer
                if sentence_buffer.strip():
                    await manager.send_json(websocket, {
                        "type": "sentence",
                        "content": sentence_buffer.strip(),
                    })

                # Store in memory
                memory.add_turn(session_id, "user", message)
                memory.add_turn(session_id, "assistant", full_content)

                total_ms = (time.time() - start_time) * 1000
                await manager.send_json(websocket, {
                    "type": "done",
                    "content": full_content,
                    "latency_ms": round(total_ms, 1),
                })
            else:
                result = await chat_service.chat_completion(
                    context_messages, model=model, temperature=temperature
                )
                memory.add_turn(session_id, "user", message)
                memory.add_turn(session_id, "assistant", result["content"])

                await manager.send_json(websocket, {
                    "type": "done",
                    "content": result["content"],
                    "tokens": result.get("tokens", 0),
                    "latency_ms": result.get("latency_ms", 0),
                    "provider": result.get("provider", "unknown"),
                    "model": result.get("model", "unknown"),
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, "chat")
    except Exception as e:
        try:
            await manager.send_json(websocket, {"type": "error", "message": str(e)})
        except Exception:
            pass
        manager.disconnect(websocket, "chat")


# ---- TTS WebSocket ----

@router.websocket("/ws/tts")
async def websocket_tts(websocket: WebSocket):
    """
    Real-time TTS streaming.
    Client sends: {"text": "Hello world", "voice": "en-US-GuyNeural"}
    Server sends: binary audio chunks.
    """
    await manager.connect(websocket, "tts")
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            text = data.get("text", "")
            voice = data.get("voice")

            if not tts_service.is_available():
                await websocket.send_json({"type": "error", "message": "TTS not available"})
                continue

            async for audio_chunk in tts_service.stream_speech(text, voice):
                await websocket.send_bytes(audio_chunk)

            await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, "tts")
    except Exception:
        manager.disconnect(websocket, "tts")


# ---- Avatar WebSocket ----

@router.websocket("/ws/avatar")
async def websocket_avatar(websocket: WebSocket):
    """
    Real-time avatar frame streaming.
    Client sends: {"text": "Hello", "avatar_id": "default"}
    Server sends: JSON frames with viseme data.
    """
    await manager.connect(websocket, "avatar")
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            text = data.get("text", "")
            avatar_id = data.get("avatar_id", "default")

            async for frame in avatar_service.stream_avatar_frames(text, avatar_id):
                await websocket.send_json(frame)

            await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, "avatar")
    except Exception:
        manager.disconnect(websocket, "avatar")
