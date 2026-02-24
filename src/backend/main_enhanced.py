"""
Enhanced Main FastAPI application with RAG Integration
Integrates the enhanced Q&A RAG system with existing chatbot
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
import os
import sys

# Load environment variables from .env file
try:
    import dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        dotenv.load_dotenv(env_path)
        print(f"[OK] Loaded environment from {env_path}")
    else:
        print(f"[WARNING] .env file not found at {env_path}")
except ImportError:
    print("[WARNING] python-dotenv not installed, environment variables may not load")

# Add backend directory to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))
sys.path.insert(0, str(backend_dir.parent.parent))  # For RAG integration

from backend.config import CORS_ORIGINS, API_HOST, API_PORT, DEBUG, LLM_PROVIDER, LLM_MODEL_NAME, OPEN_SOURCE_MODE
from backend.utils.logger import setup_logger
from backend.asr import WhisperASR
from backend.tts import ModernTTS, XTTSVoiceTrainer  # Use ModernTTS (Python 3.14+ compatible)
from backend.tts.coqui_tts import OpenSourceTTS  # Open source TTS
from backend.llm import LLMInterface
from backend.llm.opensource_llm import OpenSourceLLMInterface  # Open source LLM
from backend.rag import SimpleVectorDB, Retriever, DocumentIngestor
from backend.api import health_router, chat_router, ws_router, tts_stt_router
from backend.api.chat_routes import set_llm as set_llm_chat, set_tts as set_tts_chat, set_rag as set_rag_chat
from backend.api.websocket import set_modules as set_modules_ws
from backend.api.tts_stt_routes import set_tts_module, set_stt_module, set_voice_trainer
from backend.api.speech_to_speech_routes import (
    set_stt_module as set_stt_s2s,
    set_llm_module as set_llm_s2s,
    set_tts_module as set_tts_s2s
)
from backend.api.realtime_streaming import (
    set_stt_module as set_stt_realtime,
    set_llm_module as set_llm_realtime,
    set_tts_module as set_tts_realtime,
    websocket_endpoint
)

# Enhanced RAG system imports
try:
    # from rag_integration import RAGIntegratedChat, create_rag_routes  # TODO: Implement if needed
    has_enhanced_rag = False  # Temporarily disabled
    logger = setup_logger(__name__)
    logger.info("ℹ️ Enhanced RAG system disabled (module not implemented)")
except ImportError as e:
    has_enhanced_rag = False
    logger = setup_logger(__name__)
    logger.warning(f"⚠️ Enhanced RAG system not available: {e}")
    logger.info("Run 'python setup_rag_system.py' to enable enhanced RAG")

try:
    from backend.api.speech_to_speech_routes import (
        router as speech_to_speech_router,
        set_stt_module as set_stt_s2s,
        set_llm_module as set_llm_s2s,
        set_tts_module as set_tts_s2s
    )
    has_s2s = True
except ImportError:
    has_s2s = False

try:
    from backend.api.d_id_routes import router as d_id_router
    has_d_id = True
except ImportError:
    has_d_id = False

# Global module instances
asr_module = None
tts_module = None
llm_module = None
rag_retriever = None
enhanced_rag_chat = None
voice_trainer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global asr_module, tts_module, llm_module, rag_retriever, voice_trainer, enhanced_rag_chat
    
    # Startup
    logger.info("🚀 Starting up Enhanced AI Avatar Chatbot...")
    
    # Initialize Enhanced RAG System (Priority 1) - DISABLED
    # if has_enhanced_rag:
    #     try:
    #         logger.info("🧠 Initializing Enhanced RAG system...")
    #         enhanced_rag_chat = RAGIntegratedChat()
    #         logger.info("✅ Enhanced RAG system initialized - Q&A knowledge base loaded")
    #         
    #         # Add RAG routes to the app
    #         create_rag_routes(app)
    #         logger.info("✅ Enhanced RAG API routes added")
    #         
    #     except Exception as e:
    #         logger.warning(f"⚠️ Enhanced RAG initialization failed: {e}")
    #         logger.info("Falling back to basic RAG system")
    
    try:
        # Initialize LLM - Force Groq for better responses with enhanced model
        logger.info("🤖 Initializing LLM module with Groq (Enhanced Model)...")
        
        # Use more capable model for better answers
        llm_module = LLMInterface(provider="groq", model=LLM_MODEL_NAME)
        set_llm_chat(llm_module)
        logger.info("✅ Groq LLM initialized with enhanced model for better responses")
            
    except Exception as e:
        logger.warning(f"⚠️ Groq LLM initialization failed: {e}")
        
        # Try open source fallback
        logger.info("Attempting fallback to open source Ollama...")
        try:
            llm_module = OpenSourceLLMInterface(provider="ollama", model="llama3.2:3b")
            set_llm_chat(llm_module)
            logger.info("✅ LLM fallback to Ollama initialized")
        except Exception as e2:
            logger.warning(f"⚠️ Open source LLM also failed: {e2}")
            logger.info("Using enhanced RAG system for responses")
    
    # Optional modules - don't fail startup if these fail
    try:
        # Initialize ASR (Speech-to-Text) - OpenAI Whisper
        logger.info("🎤 Initializing ASR module (Whisper)...")
        asr_module = WhisperASR(model_name="base", device="cpu")
        set_stt_module(asr_module)
        if has_s2s:
            set_stt_s2s(asr_module)
        logger.info("✅ ASR module initialized (Whisper)")
    except Exception as e:
        logger.warning(f"⚠️ ASR initialization failed (optional): {e}")
    
    try:
        # Initialize TTS (Text-to-Speech)
        logger.info("🔊 Initializing TTS module...")
        
        if OPEN_SOURCE_MODE:
            logger.info("🌟 Open Source Mode: Using Coqui TTS")
            tts_module = OpenSourceTTS(device="cpu")
            set_tts_module(tts_module)
            set_tts_chat(tts_module)
            if has_s2s:
                set_tts_s2s(tts_module)
            logger.info("✅ Coqui TTS loaded on CPU")
            logger.info("✅ Using Coqui TTS (High Quality)")
            logger.info("✅ Open Source TTS initialized")
        else:
            tts_module = ModernTTS(device="cpu")
            set_tts_module(tts_module)
            set_tts_chat(tts_module)
            if has_s2s:
                set_tts_s2s(tts_module)
            logger.info("✅ TTS module initialized")
            
    except Exception as e:
        logger.warning(f"⚠️ TTS initialization failed (optional): {e}")
        
        # Try open source fallback if not already using it
        if not OPEN_SOURCE_MODE:
            try:
                logger.info("Attempting open source TTS fallback...")
                tts_module = OpenSourceTTS(device="cpu")
                set_tts_module(tts_module)
                set_tts_chat(tts_module)
                if has_s2s:
                    set_tts_s2s(tts_module)
                logger.info("✅ Open Source TTS fallback initialized")
            except Exception as e2:
                logger.warning(f"⚠️ TTS fallback also failed: {e2}")
    
    try:
        # Initialize Voice Trainer
        logger.info("🎵 Initializing Voice Trainer...")
        voice_trainer = XTTSVoiceTrainer(device="cpu", output_dir="models/custom_voices")
        set_voice_trainer(voice_trainer)
        logger.info("✅ Voice Trainer initialized")
    except Exception as e:
        logger.warning(f"⚠️ Voice Trainer initialization failed (optional): {e}")
    
    try:
        # Initialize Basic RAG (fallback)
        logger.info("📚 Initializing basic RAG module with ChromaDB...")
        vector_db = SimpleVectorDB(db_path="./data/merged_chroma_db")
        rag_retriever = Retriever(vector_db)
        set_rag_chat(rag_retriever)
        logger.info("✅ Basic RAG module initialized with ChromaDB - ready for knowledge base queries")
    except Exception as e:
        logger.warning(f"⚠️ Basic RAG initialization failed (optional): {e}")
    
    # Set modules for WebSocket and Speech-to-Speech
    try:
        set_modules_ws(asr_module, tts_module, llm_module, rag_retriever)
    except Exception as e:
        logger.warning(f"⚠️ WebSocket module setup failed: {e}")
    
    if has_s2s and llm_module:
        try:
            set_llm_s2s(llm_module)
            logger.info("✅ Speech-to-speech LLM initialized")
        except Exception as e:
            logger.warning(f"⚠️ Speech-to-speech LLM setup failed: {e}")
    
    # Final status report
    logger.info("="*60)
    logger.info("🎉 ENHANCED AI AVATAR CHATBOT STARTUP COMPLETE!")
    logger.info("="*60)
    
    if has_enhanced_rag and enhanced_rag_chat:
        logger.info("🧠 Enhanced RAG System: ✅ Active (Q&A Knowledge Base)")
        if enhanced_rag_chat.rag_llm.rag_system:
            qa_count = len(enhanced_rag_chat.rag_llm.rag_system.qa_data)
            categories = len(enhanced_rag_chat.rag_llm.rag_system.get_category_distribution())
            logger.info(f"📊 Knowledge Base: {qa_count} Q&A pairs, {categories} categories")
    else:
        logger.info("🧠 Enhanced RAG System: ❌ Not available (basic RAG active)")
    
    logger.info(f"🤖 LLM System: {'✅ Active' if llm_module else '❌ Fallback mode'}")
    logger.info(f"🔊 TTS System: {'✅ Active' if tts_module else '❌ Not available'}")
    logger.info(f"🎤 STT System: {'✅ Active' if asr_module else '❌ Not available'}")
    
    if OPEN_SOURCE_MODE:
        logger.info("💰 Cost: $0 (100% Free & Open Source)")
    
    logger.info(f"🌐 Server: Ready at http://localhost:{API_PORT}")
    logger.info(f"📱 Chat UI: http://localhost:{API_PORT}/static/chat.html")
    logger.info("="*60)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Enhanced AI Avatar Chatbot...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Enhanced AI Avatar Chatbot API",
    description="Real-time AI chatbot with enhanced RAG, speech recognition and synthesis",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
_has_wildcard_origin = False
try:
    _has_wildcard_origin = isinstance(CORS_ORIGINS, list) and any(o.strip() == "*" for o in CORS_ORIGINS)
except Exception:
    _has_wildcard_origin = False

if _has_wildcard_origin:
    # When using wildcard origins, browsers disallow credentials.
    # Using allow_origin_regex covers any localhost port (e.g. 8080, 3000) without editing env.
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*",
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(health_router, tags=["Health"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(tts_stt_router, prefix="/api", tags=["TTS/STT"])
app.include_router(ws_router, tags=["WebSocket"])
app.websocket("/ws/realtime-speech")(websocket_endpoint)

if has_s2s:
    app.include_router(speech_to_speech_router, prefix="/api", tags=["Speech-to-Speech"])
if has_d_id:
    app.include_router(d_id_router, tags=["D-ID Avatar"])

# Enhanced RAG routes are added dynamically in lifespan

# Mount static files (frontend) 
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/")
async def root():
    """Root endpoint with enhanced information"""
    features = []
    if has_enhanced_rag:
        features.append("Enhanced RAG Q&A System")
    if asr_module:
        features.append("Speech Recognition (Whisper)")
    if tts_module:
        features.append("Text-to-Speech")
    if llm_module:
        features.append("LLM Chat")
    
    return {
        "message": "Enhanced AI Avatar Chatbot API",
        "version": "2.0.0",
        "features": features,
        "open_source_mode": OPEN_SOURCE_MODE,
        "docs": "/docs",
        "health": "/health",
        "chat_ui": "/static/chat.html",
        "rag_endpoints": {
            "chat": "/api/rag/chat",
            "search": "/api/rag/search", 
            "stats": "/api/rag/stats"
        } if has_enhanced_rag else None
    }

@app.get("/api/enhanced-status")
async def enhanced_status():
    """Get detailed system status"""
    global enhanced_rag_chat, llm_module, tts_module, asr_module
    
    status = {
        "system": "Enhanced AI Avatar Chatbot",
        "version": "2.0.0",
        "open_source_mode": OPEN_SOURCE_MODE,
        "components": {
            "enhanced_rag": {
                "available": has_enhanced_rag,
                "active": enhanced_rag_chat is not None,
                "knowledge_base_size": 0,
                "categories": 0
            },
            "llm": {
                "available": llm_module is not None,
                "provider": LLM_PROVIDER if not OPEN_SOURCE_MODE else "opensource",
                "model": LLM_MODEL_NAME
            },
            "tts": {
                "available": tts_module is not None,
                "type": "OpenSourceTTS" if OPEN_SOURCE_MODE else "ModernTTS"
            },
            "stt": {
                "available": asr_module is not None,
                "type": "Whisper"
            }
        }
    }
    
    # Add RAG details if available
    if enhanced_rag_chat and enhanced_rag_chat.rag_llm.rag_system:
        rag_system = enhanced_rag_chat.rag_llm.rag_system
        status["components"]["enhanced_rag"]["knowledge_base_size"] = len(rag_system.qa_data)
        status["components"]["enhanced_rag"]["categories"] = len(rag_system.get_category_distribution())
    
    return status

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting Enhanced AI Avatar Chatbot on {API_HOST}:{API_PORT}")
    
    if DEBUG:
        # Use import string for reload mode
        uvicorn.run(
            "backend.main_enhanced:app",
            host=API_HOST,
            port=API_PORT,
            reload=True,
            log_level="debug"
        )
    else:
        # Use app object for production
        uvicorn.run(
            app,
            host=API_HOST,
            port=API_PORT,
            reload=False,
            log_level="info"
        )