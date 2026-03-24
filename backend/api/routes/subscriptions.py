"""
Subscription & Demo Mode API Routes
Handles tier upgrades, usage tracking, and subscription management.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from datetime import datetime, timezone
from typing import Optional

from api.dependencies import get_optional_user
from api.services.subscription_manager import subscription_manager
from api.services.subscription_models import SubscriptionTier, TIER_LIMITS

router = APIRouter(tags=["Subscriptions"])


# ════════════════════════════════════════════════════════════════════
# PUBLIC ENDPOINTS (No auth required for demo)
# ════════════════════════════════════════════════════════════════════

@router.get("/api/demo/start")
async def start_demo_session(
    user_id: Optional[str] = Header(None),
    session_duration: int = 600,  # 10 seconds default
):
    """
    Start a demo session.
    Demo users get limited tokens/TTS/STT for testing.
    
    Defaults: 10 seconds session, 1000 tokens, 10 min TTS/STT
    """
    if not user_id:
        # Generate anonymous user ID
        user_id = f"demo_{datetime.now(timezone.utc).timestamp()}"
    
    demo = subscription_manager.create_demo_session(user_id, duration_seconds=session_duration)
    stats = subscription_manager.get_usage_stats(user_id)
    
    return {
        "status": "demo_started",
        "user_id": user_id,
        "tier": "demo",
        "duration_seconds": session_duration,
        "usage_stats": stats,
        "message": "Welcome to Athena AI Demo! You have 10 seconds to test our chatbot."
    }


@router.get("/api/subscription/tiers")
async def get_subscription_tiers():
    """Get all available subscription tiers and pricing."""
    tiers = []
    for tier, limits in TIER_LIMITS.items():
        tiers.append({
            "tier": tier.value,
            "name": limits["name"],
            "price": limits["price"],
            "monthly_tokens": limits["monthly_tokens"],
            "tts_minutes": limits["tts_minutes"],
            "stt_minutes": limits["stt_minutes"],
            "daily_sessions": limits["daily_sessions"],
            "max_message_length": limits["max_message_length"],
            "duration_seconds": limits["duration_seconds"],
        })
    return {"tiers": tiers}


@router.get("/api/subscription/usage")
async def get_current_usage(
    user_id: Optional[str] = Header(None),
):
    """Get current user's usage statistics."""
    if not user_id:
        raise HTTPException(status_code=401, detail="user_id header required")
    
    stats = subscription_manager.get_usage_stats(user_id)
    return stats


# ════════════════════════════════════════════════════════════════════
# AUTHENTICATED ENDPOINTS (Require user)
# ════════════════════════════════════════════════════════════════════

@router.post("/api/subscription/upgrade")
async def upgrade_subscription(
    tier: str,
    user_id: Optional[str] = Header(None),
    user=Depends(get_optional_user)
):
    """
    Upgrade user's subscription tier.
    Available tiers: starter, pro, unlimited
    """
    if not user_id and not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = user_id or user.id if user else None
    
    try:
        new_tier = SubscriptionTier(tier)
    except ValueError:
        return {"error": f"Invalid tier. Choose from: starter, pro, unlimited"}
    
    # In production, you would:
    # 1. Process payment via Stripe/PayPal
    # 2. Create database record
    # 3. Send confirmation email
    
    subscription = subscription_manager.upgrade_tier(user_id, new_tier)
    
    return {
        "status": "upgraded",
        "user_id": user_id,
        "tier": tier,
        "price": TIER_LIMITS[new_tier]["price"],
        "expires_at": subscription["expires_at"].isoformat(),
        "message": f"Successfully upgraded to {TIER_LIMITS[new_tier]['name']}!"
    }


@router.post("/api/subscription/cancel")
async def cancel_subscription(
    user_id: Optional[str] = Header(None),
    user=Depends(get_optional_user)
):
    """Cancel subscription and revert to demo mode."""
    if not user_id and not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = user_id or user.id if user else None
    
    # Revert to demo
    subscription_manager.create_demo_session(user_id)
    
    return {
        "status": "cancelled",
        "message": "Subscription cancelled. Reverted to demo mode.",
        "user_id": user_id,
    }


@router.get("/api/subscription/status")
async def get_subscription_status(
    user_id: Optional[str] = Header(None),
    user=Depends(get_optional_user)
):
    """Get current subscription status."""
    if not user_id and not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = user_id or user.id if user else None
    sub = subscription_manager.get_subscription(user_id)
    stats = subscription_manager.get_usage_stats(user_id)
    
    return {
        "user_id": user_id,
        "tier": sub["tier"].value,
        "tier_name": TIER_LIMITS[sub["tier"]]["name"],
        "is_demo": subscription_manager.is_demo_user(user_id),
        "expires_at": sub["expires_at"].isoformat() if sub["expires_at"] else None,
        "usage": stats,
        "session_expired": subscription_manager.is_session_expired(user_id),
    }


@router.post("/api/subscription/reset-demo")
async def reset_demo_session(
    user_id: Optional[str] = Header(None),
):
    """Reset demo session (for testing)."""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id header required")
    
    subscription_manager.create_demo_session(user_id, duration_seconds=600)
    stats = subscription_manager.get_usage_stats(user_id)
    
    return {
        "status": "demo_reset",
        "message": "Demo session reset. You have 10 seconds again.",
        "usage_stats": stats,
    }
