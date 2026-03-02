"""
Chatbot CRUD routes — create, read, update, delete chatbot instances.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from api.core.database import get_db
from api.dependencies import get_current_user
from api.models.models import User, Chatbot
from api.schemas.schemas import ChatbotCreate, ChatbotUpdate, ChatbotResponse

router = APIRouter(prefix="/api/chatbots", tags=["Chatbots"])


@router.get("/", response_model=List[ChatbotResponse])
async def list_chatbots(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Chatbot).where(Chatbot.owner_id == user.id).order_by(Chatbot.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=ChatbotResponse, status_code=status.HTTP_201_CREATED)
async def create_chatbot(
    body: ChatbotCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chatbot = Chatbot(
        owner_id=user.id,
        name=body.name,
        system_prompt=body.system_prompt,
        llm_model=body.llm_model,
        voice_id=body.voice_id,
        avatar_id=body.avatar_id,
        temperature=body.temperature,
        max_tokens=body.max_tokens,
    )
    db.add(chatbot)
    await db.flush()
    await db.refresh(chatbot)
    return chatbot


@router.get("/{chatbot_id}", response_model=ChatbotResponse)
async def get_chatbot(
    chatbot_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Chatbot).where(Chatbot.id == chatbot_id, Chatbot.owner_id == user.id)
    )
    chatbot = result.scalar_one_or_none()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return chatbot


@router.patch("/{chatbot_id}", response_model=ChatbotResponse)
async def update_chatbot(
    chatbot_id: str,
    body: ChatbotUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Chatbot).where(Chatbot.id == chatbot_id, Chatbot.owner_id == user.id)
    )
    chatbot = result.scalar_one_or_none()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(chatbot, key, value)

    await db.flush()
    await db.refresh(chatbot)
    return chatbot


@router.delete("/{chatbot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chatbot(
    chatbot_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Chatbot).where(Chatbot.id == chatbot_id, Chatbot.owner_id == user.id)
    )
    chatbot = result.scalar_one_or_none()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    await db.delete(chatbot)
