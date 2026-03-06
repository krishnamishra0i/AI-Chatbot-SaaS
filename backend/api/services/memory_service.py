"""
Memory & Intelligence Service — conversation buffer + context management.

Provides:
  - Short-term memory (in-memory conversation buffer per session)
  - Conversation summarisation for context trimming
  - Hooks for future long-term vector DB integration
"""

import asyncio
from typing import Dict, List, Optional
from collections import deque
from datetime import datetime

from api.core.config import get_settings

settings = get_settings()


class ConversationMemory:
    """
    In-memory conversation buffer with sliding window.
    Keeps the last N turns per session for context injection.
    """

    def __init__(self, max_turns: int = None):
        self.max_turns = max_turns or settings.MEMORY_BUFFER_SIZE
        self._sessions: Dict[str, deque] = {}
        self._metadata: Dict[str, dict] = {}

    def get_or_create(self, session_id: str) -> deque:
        if session_id not in self._sessions:
            self._sessions[session_id] = deque(maxlen=self.max_turns)
            self._metadata[session_id] = {
                "created_at": datetime.utcnow().isoformat(),
                "turn_count": 0,
            }
        return self._sessions[session_id]

    def add_turn(self, session_id: str, role: str, content: str):
        """Add a conversation turn (user or assistant)."""
        buf = self.get_or_create(session_id)
        buf.append({"role": role, "content": content})
        self._metadata[session_id]["turn_count"] += 1

    def get_messages(self, session_id: str) -> List[dict]:
        """Get conversation history as OpenAI-format messages."""
        buf = self.get_or_create(session_id)
        return list(buf)

    def get_context_window(
        self,
        session_id: str,
        system_prompt: str,
        user_message: str,
    ) -> List[dict]:
        """
        Build a full context window:
          [system] + [history] + [current user message]
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.get_messages(session_id))
        messages.append({"role": "user", "content": user_message})
        return messages

    def clear_session(self, session_id: str):
        self._sessions.pop(session_id, None)
        self._metadata.pop(session_id, None)

    def get_session_info(self, session_id: str) -> dict:
        meta = self._metadata.get(session_id, {})
        buf = self._sessions.get(session_id, deque())
        return {
            "session_id": session_id,
            "turns": len(buf),
            "max_turns": self.max_turns,
            **meta,
        }

    def list_sessions(self) -> List[dict]:
        return [self.get_session_info(sid) for sid in self._sessions]

    def summarise_session(self, session_id: str) -> str:
        """
        Create a text summary of the conversation.
        Useful for context trimming or long-term storage.
        """
        buf = self._sessions.get(session_id, deque())
        if not buf:
            return ""
        lines = []
        for msg in buf:
            role = msg["role"].capitalize()
            lines.append(f"{role}: {msg['content'][:200]}")
        return "\n".join(lines)


# ─── Singleton ────────────────────────────────────────
_memory = None


def get_memory() -> ConversationMemory:
    global _memory
    if _memory is None:
        _memory = ConversationMemory()
    return _memory
