"""
Chat Storage Service — Save and retrieve chat messages from MongoDB/SQLite
Integrates with ChatSession and ChatMessage models
"""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from api.models.models import ChatSession, ChatMessage

class ChatStorageService:
    """Store and retrieve chat messages per user"""
    
    @staticmethod
    async def save_message(
        db: AsyncSession,
        session_id: str,
        user_identifier: str,
        chatbot_id: str,
        role: str,
        content: str,
        tokens: int = 0,
        latency_ms: float = None,
    ):
        """
        Save a single chat message
        
        Args:
            db: Database session
            session_id: Chat session ID (chatbot_id by default)
            user_identifier: User ID from JWT (or anonymous session)
            chatbot_id: ID of the chatbot
            role: "user" or "assistant" or "system"
            content: Message text
            tokens: Token count for this message
            latency_ms: Response time in milliseconds
            
        Returns:
            ChatMessage object
        """
        try:
            # Get or create chat session
            stmt = select(ChatSession).where(
                and_(
                    ChatSession.id == session_id,
                    ChatSession.chatbot_id == chatbot_id,
                )
            )
            result = await db.execute(stmt)
            session = result.scalar_one_or_none()
            
            if not session:
                # Create new session
                session = ChatSession(
                    id=session_id,
                    chatbot_id=chatbot_id,
                    user_identifier=user_identifier,
                    started_at=datetime.now(timezone.utc),
                )
                db.add(session)
                await db.flush()
            
            # Create message
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                tokens=tokens,
                latency_ms=latency_ms,
                created_at=datetime.now(timezone.utc),
            )
            db.add(message)
            
            # Update session stats
            session.message_count = (session.message_count or 0) + 1
            session.tokens_used = (session.tokens_used or 0) + tokens
            
            await db.commit()
            return message
            
        except Exception as e:
            print(f"Error saving message: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def get_user_chat_history(
        db: AsyncSession,
        user_identifier: str,
        limit: int = 100,
        offset: int = 0,
    ):
        """
        Get all chat messages for a user
        
        Args:
            db: Database session
            user_identifier: User ID from JWT
            limit: Max messages to return
            offset: Pagination offset
            
        Returns:
            List of ChatMessage objects with session info
        """
        try:
            # Get sessions for user
            stmt = (
                select(ChatSession)
                .where(ChatSession.user_identifier == user_identifier)
                .options(selectinload(ChatSession.messages))
                .order_by(ChatSession.started_at.desc())
            )
            result = await db.execute(stmt)
            sessions = result.unique().scalars().all()
            
            # Flatten messages
            all_messages = []
            for session in sessions:
                for msg in session.messages:
                    msg_dict = {
                        'id': msg.id,
                        'content': msg.content,
                        'role': msg.role,
                        'tokens': msg.tokens,
                        'created_at': msg.created_at.isoformat() if msg.created_at else None,
                        'session_id': session.id,
                        'chatbot_id': session.chatbot_id,
                        'session_started': session.started_at.isoformat() if session.started_at else None,
                    }
                    all_messages.append(msg_dict)
            
            # Apply pagination
            return all_messages[offset:offset+limit]
            
        except Exception as e:
            print(f"Error fetching chat history: {e}")
            raise

    @staticmethod
    async def get_session_messages(
        db: AsyncSession,
        session_id: str,
    ):
        """
        Get all messages in a specific chat session
        """
        try:
            stmt = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc())
            )
            result = await db.execute(stmt)
            messages = result.scalars().all()
            
            return [
                {
                    'id': msg.id,
                    'content': msg.content,
                    'role': msg.role,
                    'tokens': msg.tokens,
                    'created_at': msg.created_at.isoformat() if msg.created_at else None,
                }
                for msg in messages
            ]
        except Exception as e:
            print(f"Error fetching session messages: {e}")
            raise

    @staticmethod
    async def delete_session(
        db: AsyncSession,
        session_id: str,
        user_identifier: str,
    ):
        """
        Delete a chat session (only by owner)
        """
        try:
            stmt = select(ChatSession).where(
                and_(
                    ChatSession.id == session_id,
                    ChatSession.user_identifier == user_identifier,
                )
            )
            result = await db.execute(stmt)
            session = result.scalar_one_or_none()
            
            if not session:
                return False
            
            await db.delete(session)
            await db.commit()
            return True
            
        except Exception as e:
            print(f"Error deleting session: {e}")
            await db.rollback()
            raise

# Singleton instance
chat_storage = ChatStorageService()
