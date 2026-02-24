"""
Health check and status endpoints
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "AI Avatar Chatbot API is running"
    }

@router.get("/status")
async def status():
    """Get system status"""
    return {
        "status": "running",
        "service": "AI Avatar Chatbot",
        "version": "1.0.0"
    }
