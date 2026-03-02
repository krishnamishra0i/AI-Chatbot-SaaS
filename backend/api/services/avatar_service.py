"""
Avatar & Lip-Sync service stub.
Handles phoneme extraction, avatar rendering pipeline.
"""

import asyncio
from typing import Optional, AsyncGenerator


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


async def generate_visemes(text: str) -> list:
    """
    Generate viseme (mouth shape) data from text for lip-sync.
    In production, this would use a phoneme-to-viseme mapper.
    """
    # Stub: returns a sequence of viseme IDs mapped from text length
    viseme_map = ["sil", "aa", "eh", "ih", "oh", "oo", "ss", "th", "ff", "pp", "nn"]
    visemes = []
    duration_ms = 80  # ms per viseme
    for i, char in enumerate(text):
        idx = ord(char) % len(viseme_map)
        visemes.append({
            "viseme": viseme_map[idx],
            "offset_ms": i * duration_ms,
            "duration_ms": duration_ms,
        })
    return visemes


async def stream_avatar_frames(
    text: str,
    avatar_id: str = "default",
) -> AsyncGenerator[dict, None]:
    """
    Stream avatar animation frames.
    Each frame contains viseme data + optional pose info.
    In production this would render actual frames or drive a WebRTC stream.
    """
    visemes = await generate_visemes(text)
    for v in visemes:
        yield {
            "type": "avatar_frame",
            "avatar_id": avatar_id,
            "viseme": v["viseme"],
            "offset_ms": v["offset_ms"],
            "duration_ms": v["duration_ms"],
        }
        await asyncio.sleep(v["duration_ms"] / 1000.0)
