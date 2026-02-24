"""
Enhanced Main FastAPI application with RAG Integration
Integrates the enhanced Q&A RAG system with existing chatbot
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
import os
import sys

# Load environment variables from .env file
try:
    import dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        dotenv.load_dotenv(env_path)
        print(f"Loaded environment from {env_path}")
    else:
        print(f".env file not found at {env_path}")
except ImportError:
    print("python-dotenv not installed, environment variables may not load")

# Add backend directory to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))
sys.path.insert(0, str(backend_dir.parent.parent))  # For RAG integration

from backend.config import CORS_ORIGINS, API_HOST, API_PORT, DEBUG, LLM_PROVIDER, LLM_MODEL_NAME, OPEN_SOURCE_MODE
from backend.utils.logger import setup_logger
from backend.api.chat_routes import router as chat_router

# Create FastAPI app
app = FastAPI(
    title="AI Avatar Chatbot API",
    description="Enhanced AI Avatar Chatbot with RAG Integration",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Avatar Chatbot API v2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    print(f"Starting server on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT, reload=DEBUG)