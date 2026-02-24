"""
Main FastAPI application for AI Avatar Chatbot
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
from contextlib import asynccontextmanager
import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Environment variables loaded from .env file")
except ImportError:
    print("[WARN] python-dotenv not installed, using system environment variables")

# Add backend directory to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))

from backend.config import CORS_ORIGINS, API_HOST, API_PORT, DEBUG, LLM_PROVIDER, LLM_MODEL_NAME, OPEN_SOURCE_MODE
from backend.utils.logger import setup_logger
from backend.asr import WhisperASR
from backend.tts import ModernTTS, XTTSVoiceTrainer  # Use ModernTTS (Python 3.14+ compatible)
from backend.tts.coqui_tts import OpenSourceTTS  # Open source TTS
from backend.llm import LLMInterface
from backend.llm.opensource_llm import OpenSourceLLMInterface  # Open source LLM
from backend.rag import SimpleVectorDB, Retriever, DocumentIngestor
from backend.rag.simple_qa_retriever import SimpleQARetriever
try:
    from backend.rag.enhanced_retriever import EnhancedRetriever
    has_enhanced_rag = True
except ImportError:
    has_enhanced_rag = False
try:
    from backend.rag.semantic_retriever import SemanticRetriever
    has_semantic_retriever = True
except Exception:
    SemanticRetriever = None
    has_semantic_retriever = False
from backend.api import health_router, chat_router, ws_router, tts_stt_router, rag_admin_router
from backend.api.chat_routes import set_llm as set_llm_chat, set_tts as set_tts_chat, set_rag as set_rag_chat
from backend.api.websocket import set_modules as set_modules_ws
from backend.api.tts_stt_routes import set_tts_module, set_stt_module, set_voice_trainer
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

logger = setup_logger(__name__)

# Global module instances
asr_module = None
tts_module = None
llm_module = None
rag_retriever = None
voice_trainer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global asr_module, tts_module, llm_module, rag_retriever, voice_trainer
    
    # Startup
    logger.info("Starting up AI Avatar Chatbot...")
    
    try:
        # Initialize LLM - Use open source if enabled
        logger.info("Initializing LLM module...")
        
        if OPEN_SOURCE_MODE:
            logger.info("🌟 Open Source Mode: Using local Ollama LLM")
            llm_module = OpenSourceLLMInterface(provider="ollama", model=LLM_MODEL_NAME)
            set_llm_chat(llm_module)
            logger.info(f"✅ Open Source LLM initialized: {LLM_MODEL_NAME}")
        else:
            llm_module = LLMInterface(provider=LLM_PROVIDER, model=LLM_MODEL_NAME)
            set_llm_chat(llm_module)
            logger.info(f"✅ LLM module initialized with {LLM_PROVIDER.upper()} (Model: {LLM_MODEL_NAME})")
            
    except Exception as e:
        logger.warning(f"⚠️  Primary LLM initialization failed: {e}")
        
        # Try open source fallback
        if not OPEN_SOURCE_MODE:
            logger.info("Attempting fallback to open source Ollama...")
            try:
                llm_module = OpenSourceLLMInterface(provider="ollama", model="llama3.2:3b")
                set_llm_chat(llm_module)
                logger.info("✅ LLM fallback to Ollama initialized")
            except Exception as e2:
                logger.warning(f"⚠️  Open source LLM also failed: {e2}")
                logger.info("Using basic chat fallback")
        else:
            logger.warning(f"⚠️  Open source LLM initialization failed: {e}")
            logger.info("Using basic chat fallback")
    
    # Optional modules - don't fail startup if these fail
    try:
        # Initialize ASR (Speech-to-Text) - OpenAI Whisper
        logger.info("Initializing ASR module (Whisper)...")
        asr_module = WhisperASR(model_name="base", device="cpu")
        set_stt_module(asr_module)
        if has_s2s:
            set_stt_s2s(asr_module)
        logger.info("✅ ASR module initialized (Whisper)")
    except Exception as e:
        logger.warning(f"⚠️  ASR initialization failed (optional): {e}")
    
    try:
        # Initialize TTS (Text-to-Speech)
        logger.info("Initializing TTS module...")
        
        if OPEN_SOURCE_MODE:
            logger.info("🌟 Open Source Mode: Using Coqui TTS")
            tts_module = OpenSourceTTS(device="cpu")
            set_tts_module(tts_module)
            set_tts_chat(tts_module)  # Also set for chat routes
            if has_s2s:
                set_tts_s2s(tts_module)
            logger.info("✅ Open Source TTS initialized")
        else:
            tts_module = ModernTTS(device="cpu")  # ModernTTS uses edge-tts (Python 3.14 compatible)
            set_tts_module(tts_module)
            set_tts_chat(tts_module)  # Also set for chat routes
            if has_s2s:
                set_tts_s2s(tts_module)
            logger.info("✅ TTS module initialized")
            
    except Exception as e:
        logger.warning(f"⚠️  TTS initialization failed (optional): {e}")
        
        # Try fallback: if OPEN_SOURCE_MODE failed, attempt ModernTTS; otherwise try OpenSourceTTS
        if OPEN_SOURCE_MODE:
            try:
                logger.info("Attempting fallback to ModernTTS (edge-tts/pyttsx3)...")
                tts_module = ModernTTS(device="cpu")
                set_tts_module(tts_module)
                set_tts_chat(tts_module)
                if has_s2s:
                    set_tts_s2s(tts_module)
                logger.info("✅ ModernTTS fallback initialized")
            except Exception as e2:
                logger.warning(f"⚠️  ModernTTS fallback also failed: {e2}")
        else:
            try:
                logger.info("Attempting open source TTS fallback...")
                tts_module = OpenSourceTTS(device="cpu")
                set_tts_module(tts_module)
                set_tts_chat(tts_module)
                if has_s2s:
                    set_tts_s2s(tts_module)
                logger.info("✅ Open Source TTS fallback initialized")
            except Exception as e2:
                logger.warning(f"⚠️  TTS fallback also failed: {e2}")
    
    try:
        # Initialize Voice Trainer
        logger.info("Initializing Voice Trainer...")
        voice_trainer = XTTSVoiceTrainer(device="cpu", output_dir="models/custom_voices")
        set_voice_trainer(voice_trainer)
        logger.info("✅ Voice Trainer initialized")
    except Exception as e:
        logger.warning(f"⚠️  Voice Trainer initialization failed (optional): {e}")
    
    try:
        logger.info("Initializing RAG Knowledge Base...")

        # Try semantic retriever first
        if has_semantic_retriever and SemanticRetriever is not None:
            try:
                rag_retriever = SemanticRetriever()
                rag_retriever.build_index()
                if getattr(rag_retriever, 'is_loaded', False):
                    stats = rag_retriever.get_stats() if hasattr(rag_retriever, 'get_stats') else {'total_qa_pairs': len(getattr(rag_retriever, 'qa_data', []))}
                    set_rag_chat(rag_retriever)
                    logger.info(f"✅ Semantic RAG loaded - {stats.get('total_qa_pairs', 'unknown')} Q&A pairs")
                else:
                    logger.info("Semantic retriever loaded but no data; falling back to SimpleQARetriever")
            except Exception as e:
                logger.warning(f"Semantic retriever init failed: {e}")

        # Fallback to SimpleQARetriever
        if not rag_retriever:
            try:
                rag_retriever = SimpleQARetriever()
                if getattr(rag_retriever, 'is_loaded', False):
                    stats = rag_retriever.get_stats()
                    set_rag_chat(rag_retriever)
                    logger.info(f"✅ Knowledge Base loaded - {stats['total_qa_pairs']} Q&A pairs")
                    logger.info(f"📂 Categories: {list(stats['categories'].keys())}")
                else:
                    # Try enhanced retriever as a last fallback
                    if has_enhanced_rag:
                        try:
                            rag_retriever = EnhancedRetriever()
                            if getattr(rag_retriever, 'is_loaded', False):
                                stats = rag_retriever.get_stats()
                                set_rag_chat(rag_retriever)
                                logger.info(f"✅ Enhanced RAG loaded - {stats['total_qa_pairs']} Q&A pairs")
                            else:
                                logger.warning("No knowledge base available")
                        except Exception as e:
                            logger.warning(f"Enhanced RAG init failed: {e}")
                    else:
                        logger.warning("No knowledge base available")
            except Exception as e:
                logger.warning(f"SimpleQARetriever init failed: {e}")

    except Exception as e:
        logger.warning(f"RAG initialization error: {e}")
    
    # Set modules for WebSocket and Speech-to-Speech
    try:
        set_modules_ws(asr_module, tts_module, llm_module, rag_retriever)
    except Exception as e:
        logger.warning(f"⚠️  WebSocket module setup failed: {e}")
    
    if has_s2s and llm_module:
        try:
            set_llm_s2s(llm_module)
            logger.info("✅ Speech-to-speech LLM initialized")
        except Exception as e:
            logger.warning(f"⚠️  Speech-to-speech LLM setup failed: {e}")
    
    logger.info("✅ Startup complete!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Avatar Chatbot...")
    # Add any cleanup code here

# Create FastAPI app with lifespan
app = FastAPI(
    title="AI Avatar Chatbot API",
    description="Real-time AI chatbot with speech recognition and synthesis",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
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
app.include_router(rag_admin_router, prefix="/api", tags=["RAG Admin"])
if has_s2s:
    app.include_router(speech_to_speech_router, prefix="/api", tags=["Speech-to-Speech"])
if has_d_id:
    app.include_router(d_id_router, tags=["D-ID Avatar"])
app.include_router(ws_router, tags=["WebSocket"])

# Mount static files (frontend)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - redirect to simple chat"""
    chat_path = frontend_path / "simple_chat.html"
    if chat_path.exists():
        with open(chat_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return """
        <html>
            <head><title>AI Chatbot</title></head>
            <body>
                <h1>AI Chatbot API</h1>
                <p><a href="/docs">View API Documentation</a></p>
                <p><a href="/health">Health Check</a></p>
                <p><strong>Chat interface not found.</strong> File: simple_chat.html</p>
            </body>
        </html>
        """

@app.get("/chat", response_class=HTMLResponse)
async def chat():
    """Chat endpoint - serve the chat interface"""
    return await root()

@app.get("/premium_chatbot.html", response_class=HTMLResponse)
async def premium_chat():
    """Premium chat interface"""
    chat_path = frontend_path / "premium_chatbot.html"
    if chat_path.exists():
        with open(chat_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return await root()

@app.get("/simple_chat.html", response_class=HTMLResponse)
async def simple_chat_endpoint():
    """Simple chat interface"""
    return await root()

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    )
