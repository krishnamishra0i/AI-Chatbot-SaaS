"""
WebSocket endpoints — real-time chat, TTS streaming, avatar frames.
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set

from api.services import chat_service, tts_service, avatar_service

router = APIRouter()

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


# ---- Chat WebSocket ----

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    Real-time chat via WebSocket.
    Client sends: {"message": "Hello", "session_id": "...", "stream": true}
    Server sends: {"type": "chunk", "content": "..."} or {"type": "done", "content": "..."}
    """
    await manager.connect(websocket, "chat")
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            message = data.get("message", "")
            stream = data.get("stream", True)

            messages = [{"role": "user", "content": message}]

            if stream:
                full_content = ""
                async for chunk in chat_service.chat_completion_stream(messages):
                    full_content += chunk
                    await manager.send_json(websocket, {
                        "type": "chunk",
                        "content": chunk,
                    })
                await manager.send_json(websocket, {
                    "type": "done",
                    "content": full_content,
                })
            else:
                result = await chat_service.chat_completion(messages)
                await manager.send_json(websocket, {
                    "type": "done",
                    "content": result["content"],
                    "tokens": result.get("tokens", 0),
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
