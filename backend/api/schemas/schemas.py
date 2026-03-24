"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ── Auth ─────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class OAuthCallbackRequest(BaseModel):
    code: str
    provider: str


# ── User ─────────────────────────────────────────────

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    plan: str
    avatar_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None


# ── Chatbot ──────────────────────────────────────────

class ChatbotCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    system_prompt: Optional[str] = None
    llm_model: str = "gpt-3.5-turbo"
    voice_id: str = "en-US-GuyNeural"
    avatar_id: Optional[str] = None
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1024, ge=64, le=8192)


class ChatbotUpdate(BaseModel):
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    llm_model: Optional[str] = None
    voice_id: Optional[str] = None
    avatar_id: Optional[str] = None
    status: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class ChatbotResponse(BaseModel):
    id: str
    name: str
    system_prompt: Optional[str]
    llm_model: str
    voice_id: str
    avatar_id: Optional[str]
    status: str
    temperature: float
    max_tokens: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── API Key ──────────────────────────────────────────

class ApiKeyCreate(BaseModel):
    name: str = "Default Key"


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    is_active: bool
    last_used_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreatedResponse(ApiKeyResponse):
    """Returned only on creation — includes the full key."""
    full_key: str


# ── Chat ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    chatbot_id: Optional[str] = None
    session_id: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024
    stream: bool = False
    prompt_template: Optional[str] = None
    emotion: str = "neutral"


class ChatResponse(BaseModel):
    message: str
    session_id: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    model: str = "unknown"
    provider: str = "unknown"
    timestamp: datetime


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible /v1/chat/completions format."""
    model: str = "gpt-3.5-turbo"
    messages: List[dict]
    temperature: float = 0.7
    max_tokens: int = 1024
    stream: bool = False


# ── TTS ──────────────────────────────────────────────

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice: str = "nova"  # OpenAI voices
    speed: Optional[float | str] = None  # Accept both numeric and legacy string values
    pitch: Optional[float | str] = None  # Accept both numeric and legacy string values
    base64: bool = False
    model: Optional[str] = None  # Optional model override


class TTSResponse(BaseModel):
    audio: str  # base64 encoded
    format: str = "mp3"
    voice: str


class VoiceInfo(BaseModel):
    name: str
    short_name: str
    locale: str
    gender: str


# ── STT ──────────────────────────────────────────────

class STTResponse(BaseModel):
    text: str
    language: str = "en"
    segments: List[dict] = []


# ── Avatar ───────────────────────────────────────────

class AvatarStreamRequest(BaseModel):
    audio_data: Optional[str] = None  # base64 audio
    text: Optional[str] = None
    avatar_id: str = "default"


# ── Usage & Analytics ────────────────────────────────

class UsageSummary(BaseModel):
    total_messages: int = 0
    total_tokens: int = 0
    total_audio_seconds: float = 0.0
    total_sessions: int = 0
    total_cost: float = 0.0
    period: str = "current_month"


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    max_tokens: int
    supports_streaming: bool = True


# Rebuild forward refs
TokenResponse.model_rebuild()
