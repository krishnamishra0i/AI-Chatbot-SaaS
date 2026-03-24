"""
Athena AI Avatar Chatbot SaaS — FastAPI Application
====================================================
Production-ready entrypoint with CORS, lifespan, and all routers.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.core.config import get_settings
from api.core.database import init_db
from api.core.mongodb import connect_to_mongo, close_mongo_connection

# ---- Route imports ----
from api.routes import otp_auth, chat, tts, stt, chatbots, api_keys, avatar, models, usage, auth_proxy, subscriptions, chat_history
from api.routes import oauth, test_debug, realtime_audio
from api.websocket import handlers as ws_handlers
from api.middleware.rate_limiter import RateLimitMiddleware

settings = get_settings()

# ---- Logging ----
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("athena")


# ---- Lifespan (startup/shutdown) ----

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Athena AI backend...")
    # Initialize SQLAlchemy database (creates tables)
    await init_db()
    logger.info("✅ SQLAlchemy database initialized")
    # Initialize MongoDB
    await connect_to_mongo()
    logger.info("✅ MongoDB connected")
    yield
    logger.info("👋 Shutting down Athena AI backend")
    await close_mongo_connection()


# ---- Create FastAPI app ----

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-time AI Avatar Chatbot SaaS Platform — LLM, TTS, STT, Avatar, WebSocket",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ---- Rate Limiting ---- (add AFTER CORS will be added below)
app.add_middleware(RateLimitMiddleware)

# ---- CORS (must be LAST added, so it's FIRST in the chain) ----
# Note: add_middleware adds in reverse order, so add CORS last to make it first
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
# Ensure localhost:3000 is always included
if "http://localhost:3000" not in origins:
    origins.append("http://localhost:3000")

logger.info(f"CORS Allowed Origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)


# ---- Mount Routers ----

app.include_router(otp_auth.router)  # OTP-only passwordless authentication
app.include_router(auth_proxy.router)  # Proxy to Node.js auth-service
app.include_router(subscriptions.router)  # Subscription & demo mode
app.include_router(chat.router)
app.include_router(chat_history.router)  # Chat history & storage
app.include_router(tts.router)
app.include_router(stt.router)
app.include_router(realtime_audio.router)  # Real-time audio streaming (WebSocket)
app.include_router(chatbots.router)
app.include_router(api_keys.router)
app.include_router(avatar.router)
app.include_router(models.router)
app.include_router(oauth.router)
app.include_router(usage.router)
app.include_router(test_debug.router)  # Debug test endpoint
app.include_router(ws_handlers.router)


# ---- Root & Health ----

@app.get("/", tags=["Health"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.options("/", include_in_schema=False)
async def options_root():
    """Handle CORS preflight requests"""
    return {}


@app.get("/api/health", tags=["Health"])
async def health():
    from api.services import tts_service, stt_service
    return {
        "status": "healthy",
        "services": {
            "tts": tts_service.is_available(),
            "stt": stt_service.is_available(),
            "database": True,
        },
    }


@app.options("/api/health", include_in_schema=False)
async def options_health():
    """Handle CORS preflight requests"""
    return {}


@app.options("/{full_path:path}", include_in_schema=False)
async def options_catch_all(full_path: str):
    """Catch-all OPTIONS handler for CORS preflight requests"""
    return {}


# ---- Global Exception Handler ----

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
