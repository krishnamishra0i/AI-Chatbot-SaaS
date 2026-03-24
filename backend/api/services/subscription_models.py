"""
Usage & Subscription Database Models
Tracks token usage, TTS/STT minutes, and subscription status per user.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import enum

Base = declarative_base()


class SubscriptionTier(str, enum.Enum):
    """Subscription tiers with usage limits."""
    DEMO = "demo"           # Free 10 seconds / 1000 tokens per day
    STARTER = "starter"     # $5/month - 50K tokens/month, 60 min TTS/STT
    PRO = "pro"            # $19/month - 500K tokens/month, 600 min TTS/STT
    UNLIMITED = "unlimited" # $99/month - Unlimited


class UserSubscription:
    """
    User subscription and usage tracking.
    In production, use SQLAlchemy ORM with PostgreSQL.
    """
    def __init__(
        self,
        user_id: str,
        tier: SubscriptionTier = SubscriptionTier.DEMO,
        tokens_used: int = 0,
        tts_seconds_used: int = 0,  # Text-to-speech seconds
        stt_seconds_used: int = 0,  # Speech-to-text seconds
        is_active: bool = True,
        created_at: datetime = None,
        expires_at: datetime = None,
    ):
        self.user_id = user_id
        self.tier = tier
        self.tokens_used = tokens_used
        self.tts_seconds_used = tts_seconds_used
        self.stt_seconds_used = stt_seconds_used
        self.is_active = is_active
        self.created_at = created_at or datetime.now(timezone.utc)
        self.expires_at = expires_at


# ════════════════════════════════════════════════════════════════════
# SUBSCRIPTION TIER LIMITS
# ════════════════════════════════════════════════════════════════════

TIER_LIMITS = {
    SubscriptionTier.DEMO: {
        "name": "Demo (Free)",
        "monthly_tokens": 1000,          # 1K tokens max
        "tts_minutes": 10,               # 10 minutes TTS
        "stt_minutes": 10,               # 10 minutes STT
        "daily_sessions": 1,             # 1 session per day
        "max_message_length": 100,       # Max 100 chars per message
        "price": "$0 (Free)",
        "duration_seconds": 600,         # 10 minutes session time
    },
    SubscriptionTier.STARTER: {
        "name": "Starter",
        "monthly_tokens": 50_000,         # 50K tokens
        "tts_minutes": 60,                # 60 minutes TTS
        "stt_minutes": 60,                # 60 minutes STT
        "daily_sessions": 5,              # 5 sessions per day
        "max_message_length": 500,        # Max 500 chars per message
        "price": "$5/month",
        "duration_seconds": 3600,         # 1 hour per session
    },
    SubscriptionTier.PRO: {
        "name": "Pro",
        "monthly_tokens": 500_000,        # 500K tokens
        "tts_minutes": 600,               # 10 hours TTS
        "stt_minutes": 600,               # 10 hours STT
        "daily_sessions": 20,             # 20 sessions per day
        "max_message_length": 2000,       # Max 2000 chars
        "price": "$19/month",
        "duration_seconds": 14400,        # 4 hours per session
    },
    SubscriptionTier.UNLIMITED: {
        "name": "Unlimited",
        "monthly_tokens": 9_999_999,      # Essentially unlimited
        "tts_minutes": 9999,              # Unlimited
        "stt_minutes": 9999,              # Unlimited
        "daily_sessions": 999,            # Unlimited
        "max_message_length": 9999,       # Unlimited
        "price": "$99/month",
        "duration_seconds": 86400,        # 24 hours per session
    },
}


class UsageTracker:
    """
    Track real-time usage for active sessions.
    In production, use Redis for fast session tracking.
    """
    
    def __init__(self):
        self.active_sessions = {}  # { session_id: { tokens, tts_seconds, stt_seconds, start_time } }
    
    def start_session(self, user_id: str, tier: SubscriptionTier):
        """Start tracking a new session."""
        session_data = {
            "user_id": user_id,
            "tier": tier,
            "tokens": 0,
            "tts_seconds": 0,
            "stt_seconds": 0,
            "start_time": datetime.now(timezone.utc),
            "limits": TIER_LIMITS[tier],
        }
        self.active_sessions[user_id] = session_data
        return session_data
    
    def add_tokens(self, user_id: str, tokens: int) -> bool:
        """Add tokens to session. Returns True if within limit."""
        if user_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[user_id]
        limit = session["limits"]["monthly_tokens"]
        
        if session["tokens"] + tokens <= limit:
            session["tokens"] += tokens
            return True
        return False
    
    def add_tts_seconds(self, user_id: str, seconds: float) -> bool:
        """Add TTS seconds. Returns True if within limit."""
        if user_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[user_id]
        limit = session["limits"]["tts_minutes"] * 60
        
        if session["tts_seconds"] + seconds <= limit:
            session["tts_seconds"] += seconds
            return True
        return False
    
    def add_stt_seconds(self, user_id: str, seconds: float) -> bool:
        """Add STT seconds. Returns True if within limit."""
        if user_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[user_id]
        limit = session["limits"]["stt_minutes"] * 60
        
        if session["stt_seconds"] + seconds <= limit:
            session["stt_seconds"] += seconds
            return True
        return False
    
    def get_session_time_remaining(self, user_id: str) -> int:
        """Get remaining session time in seconds."""
        if user_id not in self.active_sessions:
            return 0
        
        session = self.active_sessions[user_id]
        elapsed = (datetime.now(timezone.utc) - session["start_time"]).total_seconds()
        max_duration = session["limits"]["duration_seconds"]
        
        return max(0, int(max_duration - elapsed))
    
    def get_usage_stats(self, user_id: str) -> dict:
        """Get current session usage stats."""
        if user_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[user_id]
        limits = session["limits"]
        
        return {
            "tier": session["tier"],
            "tokens_used": session["tokens"],
            "tokens_limit": limits["monthly_tokens"],
            "tokens_remaining": limits["monthly_tokens"] - session["tokens"],
            "tts_seconds_used": session["tts_seconds"],
            "tts_limit_seconds": limits["tts_minutes"] * 60,
            "tts_remaining_seconds": (limits["tts_minutes"] * 60) - session["tts_seconds"],
            "stt_seconds_used": session["stt_seconds"],
            "stt_limit_seconds": limits["stt_minutes"] * 60,
            "stt_remaining_seconds": (limits["stt_minutes"] * 60) - session["stt_seconds"],
            "session_time_remaining": self.get_session_time_remaining(user_id),
            "session_time_limit": limits["duration_seconds"],
        }
    
    def end_session(self, user_id: str):
        """End tracking for a session."""
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]


# Global usage tracker instance
usage_tracker = UsageTracker()
