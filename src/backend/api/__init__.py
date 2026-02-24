"""API module"""
from .health import router as health_router
from .chat_routes import router as chat_router
from .websocket import router as ws_router
from .tts_stt_routes import router as tts_stt_router
from .rag_admin import router as rag_admin_router

__all__ = ["health_router", "chat_router", "ws_router", "tts_stt_router", "rag_admin_router"]
