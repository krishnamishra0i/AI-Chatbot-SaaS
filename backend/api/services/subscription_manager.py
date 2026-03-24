"""
Subscription & Usage Management Service
Enforces limits, tracks usage, and manages demo/paid modes.
"""

from datetime import datetime, timezone, timedelta
from api.services.subscription_models import (
    SubscriptionTier,
    TIER_LIMITS,
    UsageTracker,
    usage_tracker,
)


class SubscriptionManager:
    """Manage user subscriptions and enforce limits."""
    
    def __init__(self):
        self.users_subscriptions = {}  # { user_id: { tier, expires_at } }
    
    def create_demo_session(self, user_id: str, duration_seconds: int = 600):
        """Create a 10-second demo session for anonymous user."""
        self.users_subscriptions[user_id] = {
            "tier": SubscriptionTier.DEMO,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(seconds=duration_seconds),
            "is_trial": True,
        }
        usage_tracker.start_session(user_id, SubscriptionTier.DEMO)
        return self.users_subscriptions[user_id]
    
    def upgrade_tier(self, user_id: str, new_tier: SubscriptionTier, duration_days: int = 30):
        """Upgrade user to a paid tier."""
        self.users_subscriptions[user_id] = {
            "tier": new_tier,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=duration_days),
            "is_trial": False,
        }
        usage_tracker.start_session(user_id, new_tier)
        return self.users_subscriptions[user_id]
    
    def get_subscription(self, user_id: str) -> dict:
        """Get user's current subscription."""
        if user_id not in self.users_subscriptions:
            # Create demo session if not found
            return self.create_demo_session(user_id)
        
        sub = self.users_subscriptions[user_id]
        
        # Check if subscription expired
        if sub["expires_at"] < datetime.now(timezone.utc):
            # Revert to demo
            return self.create_demo_session(user_id)
        
        return sub
    
    def is_demo_user(self, user_id: str) -> bool:
        """Check if user is in demo mode."""
        sub = self.get_subscription(user_id)
        return sub["tier"] == SubscriptionTier.DEMO
    
    def is_session_expired(self, user_id: str) -> bool:
        """Check if user's session time limit exceeded."""
        stats = usage_tracker.get_usage_stats(user_id)
        if not stats:
            return False
        return stats["session_time_remaining"] <= 0
    
    def can_use_chat(self, user_id: str, estimated_tokens: int = 100) -> tuple[bool, str]:
        """Check if user can send a chat message."""
        sub = self.get_subscription(user_id)
        tier = sub["tier"]
        limits = TIER_LIMITS[tier]
        stats = usage_tracker.get_usage_stats(user_id)
        
        # Check session expiry
        if stats["session_time_remaining"] <= 0:
            return False, f"Demo session expired. Upgrade to continue."
        
        # Check token limit
        if stats["tokens_remaining"] < estimated_tokens:
            return False, f"Token limit exceeded. {stats['tokens_remaining']} remaining."
        
        # Check message length
        return True, "OK"
    
    def can_use_tts(self, user_id: str, estimated_seconds: float) -> tuple[bool, str]:
        """Check if user can use text-to-speech."""
        sub = self.get_subscription(user_id)
        tier = sub["tier"]
        stats = usage_tracker.get_usage_stats(user_id)
        
        # Check session expiry
        if stats["session_time_remaining"] <= 0:
            return False, "Demo session expired. Upgrade to continue."
        
        # Check TTS limit
        if stats["tts_remaining_seconds"] < estimated_seconds:
            return False, f"TTS limit exceeded. {stats['tts_remaining_seconds']:.0f}s remaining."
        
        return True, "OK"
    
    def can_use_stt(self, user_id: str, estimated_seconds: float) -> tuple[bool, str]:
        """Check if user can use speech-to-text."""
        sub = self.get_subscription(user_id)
        tier = sub["tier"]
        stats = usage_tracker.get_usage_stats(user_id)
        
        # Check session expiry
        if stats["session_time_remaining"] <= 0:
            return False, "Demo session expired. Upgrade to continue."
        
        # Check STT limit
        if stats["stt_remaining_seconds"] < estimated_seconds:
            return False, f"STT limit exceeded. {stats['stt_remaining_seconds']:.0f}s remaining."
        
        return True, "OK"
    
    def add_chat_usage(self, user_id: str, tokens: int) -> bool:
        """Record chat token usage."""
        return usage_tracker.add_tokens(user_id, tokens)
    
    def add_tts_usage(self, user_id: str, seconds: float) -> bool:
        """Record TTS usage in seconds."""
        return usage_tracker.add_tts_seconds(user_id, seconds)
    
    def add_stt_usage(self, user_id: str, seconds: float) -> bool:
        """Record STT usage in seconds."""
        return usage_tracker.add_stt_seconds(user_id, seconds)
    
    def get_usage_stats(self, user_id: str) -> dict:
        """Get full usage statistics for user."""
        sub = self.get_subscription(user_id)
        stats = usage_tracker.get_usage_stats(user_id)
        
        if stats is None:
            stats = usage_tracker.start_session(user_id, sub["tier"])
        
        return {
            **stats,
            "tier_name": TIER_LIMITS[sub["tier"]]["name"],
            "subscription_expires_at": sub["expires_at"].isoformat() if sub["expires_at"] else None,
        }


# Global subscription manager instance
subscription_manager = SubscriptionManager()
