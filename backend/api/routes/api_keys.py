"""
API Key management routes.
"""

import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from api.core.database import get_db
from api.core.security import generate_api_key
from api.dependencies import get_current_user_from_auth_service
from api.models.models import User, ApiKey
from api.schemas.schemas import ApiKeyCreate, ApiKeyResponse, ApiKeyCreatedResponse

router = APIRouter(prefix="/api/keys", tags=["API Keys"])


@router.get("/", response_model=List[ApiKeyResponse])
async def list_keys(
    user: User = Depends(get_current_user_from_auth_service),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ApiKey).where(ApiKey.owner_id == user.id).order_by(ApiKey.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_key(
    body: ApiKeyCreate,
    user: User = Depends(get_current_user_from_auth_service),
    db: AsyncSession = Depends(get_db),
):
    raw_key = generate_api_key()
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    api_key = ApiKey(
        owner_id=user.id,
        key_hash=key_hash,
        key_prefix=raw_key[:12],
        name=body.name,
    )
    db.add(api_key)
    await db.flush()
    await db.refresh(api_key)

    return ApiKeyCreatedResponse.model_validate(
        {
            "id": api_key.id,
            "name": api_key.name,
            "key_prefix": api_key.key_prefix,
            "is_active": api_key.is_active,
            "last_used_at": api_key.last_used_at,
            "created_at": api_key.created_at,
            "full_key": raw_key,
        }
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_key(
    key_id: str,
    user: User = Depends(get_current_user_from_auth_service),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.owner_id == user.id)
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")

    await db.delete(key)
