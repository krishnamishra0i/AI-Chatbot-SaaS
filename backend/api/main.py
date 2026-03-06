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

# ---- Route imports ----
from api.routes import auth, chat, tts, stt, chatbots, api_keys, avatar, models, usage, auth_proxy
from api.routes import oauth
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
    await init_db()
    logger.info("✅ Database initialized")
    yield
    logger.info("👋 Shutting down Athena AI backend")


# ---- Create FastAPI app ----

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-time AI Avatar Chatbot SaaS Platform — LLM, TTS, STT, Avatar, WebSocket",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ---- CORS ----

origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Rate Limiting ----
app.add_middleware(RateLimitMiddleware)


# ---- Mount Routers ----

app.include_router(auth.router)
app.include_router(auth_proxy.router)  # Proxy to Node.js auth-service
app.include_router(chat.router)
app.include_router(tts.router)
app.include_router(stt.router)
app.include_router(chatbots.router)
app.include_router(api_keys.router)
app.include_router(avatar.router)
app.include_router(models.router)
app.include_router(oauth.router)
app.include_router(usage.router)
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


# ---- Global Exception Handler ----

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
