"""
SQLAlchemy ORM models for Athena AI.
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum

from api.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Enums ────────────────────────────────────────────

class PlanTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ChatbotStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


# ── User ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)  # nullable for OAuth users
    avatar_url = Column(String, nullable=True)
    plan = Column(SAEnum(PlanTier), default=PlanTier.FREE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # OAuth
    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, nullable=True)

    # OTP (One-Time Password) for passwordless login
    otp_code = Column(String, nullable=True)  # 6-digit OTP
    otp_expires_at = Column(DateTime, nullable=True)  # Expiration time

    # Relationships
    chatbots = relationship("Chatbot", back_populates="owner", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="owner", cascade="all, delete-orphan")


# ── Chatbot ──────────────────────────────────────────

class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(String, primary_key=True, default=_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    system_prompt = Column(Text, nullable=True)
    llm_model = Column(String, default="gpt-4o-mini")
    voice_id = Column(String, default="en-US-GuyNeural")
    avatar_id = Column(String, nullable=True)
    status = Column(SAEnum(ChatbotStatus), default=ChatbotStatus.ACTIVE)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1024)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    owner = relationship("User", back_populates="chatbots")
    sessions = relationship("ChatSession", back_populates="chatbot", cascade="all, delete-orphan")


# ── API Key ──────────────────────────────────────────

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String, nullable=False, unique=True)
    key_prefix = Column(String, nullable=False)  # first 8 chars for display
    name = Column(String, default="Default Key")
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    owner = relationship("User", back_populates="api_keys")


# ── Chat Session ─────────────────────────────────────

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=_uuid)
    chatbot_id = Column(String, ForeignKey("chatbots.id"), nullable=False)
    user_identifier = Column(String, nullable=True)  # external user or anonymous
    started_at = Column(DateTime, default=_utcnow)
    ended_at = Column(DateTime, nullable=True)
    message_count = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)

    chatbot = relationship("Chatbot", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


# ── Chat Message ─────────────────────────────────────

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    tokens = Column(Integer, default=0)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    session = relationship("ChatSession", back_populates="messages")


# ── Usage Record ─────────────────────────────────────

class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    service = Column(String, nullable=False)  # "chat", "tts", "stt", "avatar"
    tokens = Column(Integer, default=0)
    audio_seconds = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_utcnow)
