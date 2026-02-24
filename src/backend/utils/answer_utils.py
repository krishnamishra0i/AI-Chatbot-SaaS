"""
Answer post-processing utilities
"""
import re
from typing import List, Optional


def _split_sentences(text: str) -> List[str]:
    # naive sentence splitter
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def format_answer(text: str, used_kb: bool = False, sources: Optional[List[str]] = None, max_length: int = 1000) -> str:
    """Format and sanitize LLM answers for the chatbot UI - keep concise.

    - Ensures the answer starts with a clear lead sentence.
    - Keeps the response concise and trims overly long replies.
    - Appends source attribution when available.
    """
    if not text:
        return "I'm sorry — I couldn't generate an answer. Please try rephrasing your question."

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Split into sentences and build a lead
    sentences = _split_sentences(text)
    if len(sentences) == 0:
        lead = text[:150]  # Shorter lead for concise answers
        rest = text[150:]
    else:
        lead = sentences[0]
        rest = " ".join(sentences[1:])

    # If the lead is very short, try to include the next sentence
    if len(lead) < 30 and rest:
        next_sent = sentences[1] if len(sentences) > 1 else ''
        if next_sent:
            lead = f"{lead} {next_sent}"
            rest = " ".join(sentences[2:]) if len(sentences) > 2 else ''

    # Compose formatted answer - keep it simple
    formatted = lead.strip()
    if rest and len(formatted + rest) < 500:  # Only add rest if total is reasonable
        # Add a simple line break before details
        formatted = f"{formatted}\n{rest.strip()}"

    # Trim to shorter max_length for concise answers
    if len(formatted) > max_length:
        formatted = formatted[: max_length - 3].rstrip() + "..."

    # Append sources if applicable - keep minimal
    if used_kb and sources:
        try:
            src_text = ", ".join(sources)
            formatted = f"{formatted}\n\nSources: {src_text}"
        except Exception:
            pass

    return formatted
