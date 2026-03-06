"""
Avatar & Lip-Sync service.
Handles phoneme extraction and viseme generation for avatar lip-sync.
"""

import asyncio
import re
from typing import Optional, AsyncGenerator


# ── Phoneme-to-Viseme Mapping (based on MPEG-4 viseme standard) ──────

# Map English phonemes/digraphs to viseme shapes
PHONEME_VISEME_MAP = {
    # Silence
    " ": "sil",
    # Bilabial (lips together): p, b, m
    "p": "pp", "b": "pp", "m": "pp",
    # Labiodental (teeth on lip): f, v
    "f": "ff", "v": "ff",
    # Dental/Alveolar (tongue on teeth): th
    "th": "th",
    # Alveolar (tongue on ridge): t, d, n, l, s, z
    "t": "dd", "d": "dd", "n": "nn", "l": "nn",
    "s": "ss", "z": "ss",
    # Postalveolar: sh, ch, j, zh
    "sh": "ss", "ch": "ss", "j": "ss",
    # Velar/Glottal: k, g, h, ng
    "k": "kk", "g": "kk", "h": "kk", "ng": "kk",
    # Approximant: r, w, y
    "r": "rr", "w": "oo", "y": "ih",
    # Vowels
    "a": "aa", "e": "eh", "i": "ih",
    "o": "oh", "u": "oo",
    # Common digraphs
    "ee": "ih", "oo": "oo", "ou": "oh",
    "ai": "aa", "ea": "ih", "oa": "oh",
}

# Fallback mapping from character to viseme
CHAR_VISEME_FALLBACK = {
    "a": "aa", "b": "pp", "c": "kk", "d": "dd", "e": "eh",
    "f": "ff", "g": "kk", "h": "kk", "i": "ih", "j": "ss",
    "k": "kk", "l": "nn", "m": "pp", "n": "nn", "o": "oh",
    "p": "pp", "q": "kk", "r": "rr", "s": "ss", "t": "dd",
    "u": "oo", "v": "ff", "w": "oo", "x": "ss", "y": "ih",
    "z": "ss",
}


# Avatar registry
AVATARS = {
    "default": {
        "id": "default",
        "name": "Athena Default",
        "type": "2d",
        "thumbnail": "/images/paul-sir-image.png",
    },
    "paul": {
        "id": "paul",
        "name": "Paul",
        "type": "2d",
        "thumbnail": "/images/paul-sir-image.png",
    },
}


def list_avatars() -> list:
    return list(AVATARS.values())


def get_avatar(avatar_id: str) -> Optional[dict]:
    return AVATARS.get(avatar_id)


def _text_to_phonemes(text: str) -> list:
    """
    Simple rule-based text-to-phoneme conversion.
    In production, use a proper G2P (grapheme-to-phoneme) library.
    """
    text = text.lower().strip()
    phonemes = []
    i = 0
    while i < len(text):
        # Try digraphs first (2-char)
        if i + 1 < len(text):
            digraph = text[i:i+2]
            if digraph in PHONEME_VISEME_MAP:
                phonemes.append(digraph)
                i += 2
                continue

        char = text[i]
        if char.isalpha():
            phonemes.append(char)
        elif char == " ":
            phonemes.append(" ")
        # Skip punctuation
        i += 1

    return phonemes


async def generate_visemes(text: str) -> list:
    """
    Generate viseme (mouth shape) data from text for lip-sync.
    Uses phoneme-to-viseme mapping for more accurate results.
    """
    phonemes = _text_to_phonemes(text)
    visemes = []
    duration_ms = 80  # base duration per viseme

    offset = 0
    for phoneme in phonemes:
        # Look up viseme from phoneme map, then fallback
        viseme = PHONEME_VISEME_MAP.get(phoneme)
        if not viseme:
            viseme = CHAR_VISEME_FALLBACK.get(phoneme, "sil")

        # Vowels get slightly longer duration
        dur = duration_ms
        if viseme in ("aa", "eh", "ih", "oh", "oo"):
            dur = 120

        visemes.append({
            "viseme": viseme,
            "phoneme": phoneme,
            "offset_ms": offset,
            "duration_ms": dur,
        })
        offset += dur

    return visemes


async def stream_avatar_frames(
    text: str,
    avatar_id: str = "default",
) -> AsyncGenerator[dict, None]:
    """
    Stream avatar animation frames.
    Each frame contains viseme data + optional pose info.
    """
    visemes = await generate_visemes(text)
    for v in visemes:
        yield {
            "type": "avatar_frame",
            "avatar_id": avatar_id,
            "viseme": v["viseme"],
            "phoneme": v.get("phoneme", ""),
            "offset_ms": v["offset_ms"],
            "duration_ms": v["duration_ms"],
        }
        await asyncio.sleep(v["duration_ms"] / 1000.0)
