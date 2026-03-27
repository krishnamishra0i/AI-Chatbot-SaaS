"""
Application configuration using Pydantic Settings.
Reads from environment variables and .env file.
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

# Get the directory where this config file is located
CONFIG_DIR = Path(__file__).parent.parent.parent  # .../backend/
ENV_FILE = CONFIG_DIR / ".env"


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────
    APP_NAME: str = "Athena AI"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,http://localhost:3005,http://localhost:5173,http://localhost:5174"

    # ── Security ─────────────────────────────────────
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours
    JWT_SECRET: str = "athena_jwt_secret_key_change_in_prod_2026"  # Must match auth-service JWT_SECRET

    # ── Database ─────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./athena.db"

    # ── Redis ────────────────────────────────────────
    REDIS_URL: Optional[str] = None

    # ── LLM / AI ─────────────────────────────────────
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    # Chat model - COST OPTIMIZED:
    # "gpt-3.5-turbo" = CHEAPEST OpenAI (best for cost)
    # "gpt-4o-mini" = Fast + cheap (balance)
    # "groq/llama-3.3-70b-versatile" = FREE via GROQ API (if GROQ_API_KEY set)
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"  # ✅ CHEAPEST - 90% cheaper than gpt-4o
    DEFAULT_SYSTEM_PROMPT: str = "avatar_conversational"  # prompt template name

    # ── Streaming / Latency ───────────────────────────
    STREAM_CHUNK_SIZE: int = 25  # max words per TTS chunk
    TARGET_FIRST_TOKEN_MS: int = 500
    TARGET_TTS_CHUNK_MS: int = 400

    # ── Memory ───────────────────────────────────────
    MEMORY_BUFFER_SIZE: int = 20  # short-term conversation turns
    ENABLE_LONG_TERM_MEMORY: bool = False

    # ── TTS ──────────────────────────────────────────
    TTS_PROVIDER: str = "openai"  # "openai" or "edge"
    # OpenAI TTS Models (ONLY OPTIONS):
    # - "tts-1" = Low latency (50-200ms), good quality for real-time, cheaper ✅ BEST FOR REAL-TIME
    # - "tts-1-hd" = Higher quality, slower (200-500ms), more expensive
    TTS_MODEL: str = "tts-1"  # ✅ Optimized for real-time voice chat
    TTS_VOICE: str = "alloy"  # OpenAI voices: alloy, echo, fable, onyx, nova, shimmer
    TTS_SPEED: str = "+0%"  # Only for edge-tts
    TTS_PITCH: str = "+0Hz"  # Only for edge-tts

    # ── STT ──────────────────────────────────────
    # OpenAI STT Model (ONLY OPTION):
    # - "whisper-1" = Accurate speech-to-text, supports 99 languages
    # Quality options via WHISPER_MODEL parameter - COST OPTIMIZED:
    # - "tiny" = FASTEST, CHEAPEST ✅ (~100ms, good enough for real-time)
    # - "base" = Balanced quality/speed (~300ms)
    # - "small/medium/large" = Better accuracy, slower, more expensive
    WHISPER_MODEL: str = "tiny"  # ✅ CHEAPEST - Fast + Low bandwidth

    # ── OAuth ────────────────────────────────────────
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    OAUTH_REDIRECT_BASE: str = "http://localhost:5174"

    # ── Rate Limiting ────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = {
        "env_file": str(ENV_FILE),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
