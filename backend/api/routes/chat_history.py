"""
Chat History Routes — Get user's chat messages and sessions
Protected routes (require JWT authentication)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.middleware.jwt_auth import get_optional_user_from_jwt, get_current_user_from_jwt
from api.services.chat_storage_service import chat_storage

router = APIRouter(prefix="/api/chat-history", tags=["Chat History"])

@router.get("/messages")
async def get_my_chat_messages(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_optional_user_from_jwt),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    Get all chat messages for the authenticated user
    
    Query params:
    - limit: Max messages (default 100, max 1000)
    - offset: Pagination offset (default 0)
    
    Returns: List of chat messages sorted by newest first
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        messages = await chat_storage.get_user_chat_history(
            db=db,
            user_identifier=user['user_id'],
            limit=limit,
            offset=offset,
        )
        
        return {
            'status': 'success',
            'count': len(messages),
            'limit': limit,
            'offset': offset,
            'messages': messages,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch chat history: {str(e)}"
        )

@router.get("/session/{session_id}")
async def get_session_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_optional_user_from_jwt),
):
    """
    Get all messages in a specific chat session
    
    Returns: List of messages from the session, ordered by time
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        messages = await chat_storage.get_session_messages(
            db=db,
            session_id=session_id,
        )
        
        return {
            'status': 'success',
            'session_id': session_id,
            'count': len(messages),
            'messages': messages,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch session: {str(e)}"
        )

@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_optional_user_from_jwt),
):
    """
    Delete a chat session (only the owner can delete)
    
    Returns: Deletion status
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        deleted = await chat_storage.delete_session(
            db=db,
            session_id=session_id,
            user_identifier=user['user_id'],
        )
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found or not owned by user")
        
        return {
            'status': 'success',
            'message': 'Session deleted',
            'session_id': session_id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )
