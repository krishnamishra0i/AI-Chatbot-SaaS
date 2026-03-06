"""
Usage & Analytics routes — view usage data and analytics.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.dependencies import get_current_user
from api.models.models import User
from api.schemas.schemas import UsageSummary
from api.services import usage_service

router = APIRouter(prefix="/api/usage", tags=["Usage & Analytics"])


@router.get("/summary", response_model=UsageSummary)
async def get_usage_summary(
    days: int = Query(30, ge=1, le=365),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get usage summary for the authenticated user."""
    summary = await usage_service.get_usage_summary(db, user.id, days)
    return UsageSummary(**summary)


@router.get("/breakdown")
async def get_usage_breakdown(
    days: int = Query(30, ge=1, le=365),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get usage breakdown by service type."""
    breakdown = await usage_service.get_usage_by_service(db, user.id, days)
    return {"breakdown": breakdown, "period": f"last_{days}_days"}
