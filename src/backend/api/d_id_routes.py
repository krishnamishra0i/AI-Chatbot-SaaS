"""
D-ID Avatar Integration Routes
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import logging
from typing import Optional

from backend.avatar.d_id_api import get_did_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/avatar", tags=["avatar"])


@router.post("/generate-video")
async def generate_avatar_video(
    text: str,
    image_url: str = "https://api.d-id.com/example-image.jpg",
    voice_id: str = "en_US-Neural2-C"
):
    """
    Generate a D-ID talking avatar video
    
    Args:
        text: Text for the avatar to speak
        image_url: URL of the avatar image
        voice_id: D-ID voice model ID
    """
    did_client = get_did_client()
    if not did_client or not did_client.api_key:
        raise HTTPException(
            status_code=503,
            detail="D-ID API not configured. Please set D_ID_API_KEY environment variable."
        )
    
    try:
        result = await did_client.create_talking_video(
            text=text,
            image_url=image_url,
            voice_id=voice_id
        )
        if result:
            return result
        else:
            raise HTTPException(status_code=500, detail="Failed to create video")
    except Exception as e:
        logger.error(f"Error creating avatar video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/video-status/{talk_id}")
async def get_video_status(talk_id: str):
    """Get the status of a D-ID video generation"""
    did_client = get_did_client()
    if not did_client:
        raise HTTPException(status_code=503, detail="D-ID API not configured")
    
    try:
        status = await did_client.get_video_status(talk_id)
        if status:
            return status
        else:
            raise HTTPException(status_code=404, detail="Video not found")
    except Exception as e:
        logger.error(f"Error getting video status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat-with-avatar")
async def chat_with_avatar(
    message: str,
    avatar_image_url: str = "https://api.d-id.com/example-image.jpg",
    use_knowledge_base: bool = True,
    stream: bool = True
):
    """
    Chat with AI avatar - generates response and creates talking video
    
    Args:
        message: User message
        avatar_image_url: URL of avatar image
        use_knowledge_base: Whether to use RAG knowledge base
        stream: Whether to stream the response
    """
    llm = get_llm()
    rag = get_rag()
    tts = get_tts()
    did_client = get_did_client()
    
    if not llm:
        raise HTTPException(status_code=503, detail="LLM not initialized")
    if not did_client or not did_client.api_key:
        raise HTTPException(status_code=503, detail="D-ID API not configured")
    
    try:
        # Get LLM response
        if use_knowledge_base and rag:
            relevant_docs = rag.search(message, top_k=3)
            context = "\n".join([f"- {doc}" for doc in relevant_docs])
            prompt = f"Context: {context}\n\nUser: {message}"
            response = llm.generate(prompt)
            used_kb = True
        else:
            response = llm.generate(message)
            used_kb = False
        
        async def response_generator():
            """Generate streaming response with video"""
            # Send initial response
            yield json.dumps({
                "type": "text_response",
                "text": response,
                "used_knowledge_base": used_kb
            }) + "\n"
            
            # Generate avatar video
            yield json.dumps({
                "type": "status",
                "message": "Generating avatar video..."
            }) + "\n"
            
            # Stream video generation
            async for status_update in did_client.stream_video_generation(
                text=response,
                image_url=avatar_image_url
            ):
                yield json.dumps({
                    "type": "video_status",
                    **status_update
                }) + "\n"
        
        if stream:
            return StreamingResponse(
                response_generator(),
                media_type="application/x-ndjson"
            )
        else:
            # Non-streaming mode - wait for video
            result = await did_client.create_talking_video(
                text=response,
                image_url=avatar_image_url
            )
            return {
                "text_response": response,
                "video_data": result,
                "used_knowledge_base": used_kb
            }
    
    except Exception as e:
        logger.error(f"Error in chat with avatar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def set_did_module():
    """Initialize D-ID module"""
    from backend.avatar.d_id_api import get_did_client
    client = get_did_client()
    if client and client.api_key:
        logger.info("✅ D-ID module initialized")
    else:
        logger.warning("⚠️  D-ID API key not configured")
