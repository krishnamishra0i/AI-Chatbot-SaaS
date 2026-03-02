"""
Avatar & Lip-sync routes.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.services import avatar_service
from api.schemas.schemas import AvatarStreamRequest

router = APIRouter(tags=["Avatar"])


@router.get("/api/avatars")
async def list_avatars():
    """List available avatars."""
    return {"avatars": avatar_service.list_avatars()}


@router.get("/api/avatars/{avatar_id}")
async def get_avatar(avatar_id: str):
    """Get avatar details."""
    avatar = avatar_service.get_avatar(avatar_id)
    if not avatar:
        return {"error": "Avatar not found"}, 404
    return avatar


@router.post("/api/avatar/visemes")
async def get_visemes(body: AvatarStreamRequest):
    """Generate viseme data for text (for client-side lip-sync)."""
    text = body.text or ""
    visemes = await avatar_service.generate_visemes(text)
    return {"visemes": visemes, "avatar_id": body.avatar_id}


@router.post("/v1/avatar/stream")
async def stream_avatar(body: AvatarStreamRequest):
    """
    Stream avatar animation frames as NDJSON (newline-delimited JSON).
    Each line is a JSON frame with viseme data.
    """
    import json

    async def frame_stream():
        async for frame in avatar_service.stream_avatar_frames(
            text=body.text or "",
            avatar_id=body.avatar_id,
        ):
            yield json.dumps(frame) + "\n"

    return StreamingResponse(frame_stream(), media_type="application/x-ndjson")
