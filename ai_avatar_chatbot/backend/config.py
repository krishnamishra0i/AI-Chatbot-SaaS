"""
Configuration settings for the AI Avatar Chatbot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in project root
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(ENV_PATH)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"

# ASR Configuration
ASR_MODEL_NAME = os.getenv("ASR_MODEL_NAME", "base")  # tiny, base, small, medium
ASR_DEVICE = os.getenv("ASR_DEVICE", "cpu")

# TTS Configuration
TTS_MODEL_NAME = os.getenv("TTS_MODEL_NAME", "tts_models/en/ljspeech/xtts_v2")
TTS_DEVICE = os.getenv("TTS_DEVICE", "cpu")

# LLM Configuration - Auto-detect provider
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # groq (fast streaming), ollama (free), openai
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "llama-3.1-8b-instant")  # Fast Groq model
LLM_API_URL = os.getenv("LLM_API_URL", "http://localhost:11434")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Open Source Mode - Use only free models
OPEN_SOURCE_MODE = os.getenv("OPEN_SOURCE_MODE", "false").lower() == "true"
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "false").lower() == "true"

# Groq API Configuration (Real-time, fastest inference)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Get from: https://console.groq.com
GROQ_MODEL = os.getenv("GROQ_MODEL", "gemma-7b-it")  # mixtral-8x7b-32768, llama-2-70b-chat, gemma-7b-it

# RAG Configuration
VECTOR_DB_PATH = DATA_DIR / "vector_db"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
USE_RAG = os.getenv("USE_RAG", "false").lower() == "true"

# Wav2Lip Configuration
WAV2LIP_MODEL_PATH = MODELS_DIR / "wav2lip" / "checkpoints" / "wav2lip.pth"
FACE_DET_CHECKPOINT = MODELS_DIR / "wav2lip" / "face_detection" / "detection_Resnet50_Final.pth"

# Audio Configuration
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
MAX_AUDIO_LENGTH = 60  # seconds

# API Configuration
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 9999))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# WebSocket Configuration
WS_TIMEOUT = 300
MAX_CONNECTIONS = 100

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Create necessary directories
def create_directories():
    """Create necessary directories if they don't exist"""
    try:
        DATA_DIR.mkdir(exist_ok=True, parents=True)
        VECTOR_DB_PATH.mkdir(exist_ok=True, parents=True)
        KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True, parents=True)
        MODELS_DIR.mkdir(exist_ok=True, parents=True)
    except Exception as e:
        print(f"Warning: Could not create directories: {e}")

# Create directories on import
create_directories()

