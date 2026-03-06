"""
Application configuration using Pydantic Settings.
Reads from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────
    APP_NAME: str = "Athena AI"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3005,http://localhost:5173,http://localhost:5174"

    # ── Security ─────────────────────────────────────
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours

    # ── Database ─────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./athena.db"

    # ── Redis ────────────────────────────────────────
    REDIS_URL: Optional[str] = None

    # ── LLM / AI ─────────────────────────────────────
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    DEFAULT_LLM_MODEL: str = "groq/llama-3.3-70b-versatile"
    DEFAULT_SYSTEM_PROMPT: str = "avatar_conversational"  # prompt template name

    # ── Streaming / Latency ───────────────────────────
    STREAM_CHUNK_SIZE: int = 25  # max words per TTS chunk
    TARGET_FIRST_TOKEN_MS: int = 500
    TARGET_TTS_CHUNK_MS: int = 400

    # ── Memory ───────────────────────────────────────
    MEMORY_BUFFER_SIZE: int = 20  # short-term conversation turns
    ENABLE_LONG_TERM_MEMORY: bool = False

    # ── TTS ──────────────────────────────────────────
    TTS_VOICE: str = "en-US-GuyNeural"
    TTS_SPEED: str = "+0%"
    TTS_PITCH: str = "+0Hz"

    # ── STT ──────────────────────────────────────────
    WHISPER_MODEL: str = "base"

    # ── OAuth ────────────────────────────────────────
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    OAUTH_REDIRECT_BASE: str = "http://localhost:5174"

    # ── Rate Limiting ────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
