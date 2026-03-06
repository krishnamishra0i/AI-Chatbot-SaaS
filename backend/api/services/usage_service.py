"""
Usage tracking service — records API usage for analytics and billing.
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.models.models import UsageRecord, ChatSession, ChatMessage


async def record_usage(
    db: AsyncSession,
    user_id: str,
    service: str,
    tokens: int = 0,
    audio_seconds: float = 0.0,
    cost: float = 0.0,
) -> UsageRecord:
    """Record a usage event."""
    record = UsageRecord(
        user_id=user_id,
        service=service,
        tokens=tokens,
        audio_seconds=audio_seconds,
        cost=cost,
    )
    db.add(record)
    await db.flush()
    return record


async def get_usage_summary(
    db: AsyncSession,
    user_id: str,
    days: int = 30,
) -> dict:
    """Get usage summary for a user over the specified period."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(
            func.count(UsageRecord.id).label("total_records"),
            func.coalesce(func.sum(UsageRecord.tokens), 0).label("total_tokens"),
            func.coalesce(func.sum(UsageRecord.audio_seconds), 0.0).label("total_audio_seconds"),
            func.coalesce(func.sum(UsageRecord.cost), 0.0).label("total_cost"),
        ).where(
            UsageRecord.user_id == user_id,
            UsageRecord.created_at >= cutoff,
        )
    )
    row = result.one()

    # Count sessions
    sessions_result = await db.execute(
        select(func.count(ChatSession.id)).join(
            ChatSession.chatbot
        ).where(
            ChatSession.started_at >= cutoff,
        )
    )

    # Count messages for this user's usage
    messages_result = await db.execute(
        select(func.count(UsageRecord.id)).where(
            UsageRecord.user_id == user_id,
            UsageRecord.service == "chat",
            UsageRecord.created_at >= cutoff,
        )
    )

    return {
        "total_messages": messages_result.scalar() or 0,
        "total_tokens": row.total_tokens,
        "total_audio_seconds": float(row.total_audio_seconds),
        "total_sessions": 0,
        "total_cost": float(row.total_cost),
        "period": f"last_{days}_days",
    }


async def get_usage_by_service(
    db: AsyncSession,
    user_id: str,
    days: int = 30,
) -> list:
    """Get usage breakdown by service type."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(
            UsageRecord.service,
            func.count(UsageRecord.id).label("count"),
            func.coalesce(func.sum(UsageRecord.tokens), 0).label("tokens"),
            func.coalesce(func.sum(UsageRecord.audio_seconds), 0.0).label("audio_seconds"),
            func.coalesce(func.sum(UsageRecord.cost), 0.0).label("cost"),
        ).where(
            UsageRecord.user_id == user_id,
            UsageRecord.created_at >= cutoff,
        ).group_by(UsageRecord.service)
    )

    return [
        {
            "service": row.service,
            "count": row.count,
            "tokens": row.tokens,
            "audio_seconds": float(row.audio_seconds),
            "cost": float(row.cost),
        }
        for row in result.all()
    ]
