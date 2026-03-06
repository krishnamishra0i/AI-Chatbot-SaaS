"""
OAuth routes — Google OAuth2 login flow.
"""

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.core.config import get_settings
from api.core.database import get_db
from api.core.security import create_access_token
from api.models.models import User
from api.schemas.schemas import TokenResponse, UserResponse

settings = get_settings()
router = APIRouter(prefix="/api/auth/oauth", tags=["OAuth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


@router.get("/google")
async def google_oauth_start():
    """Redirect user to Google OAuth consent screen."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env",
        )

    redirect_uri = f"{settings.OAUTH_REDIRECT_BASE}/api/auth/oauth/google/callback"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url=f"{GOOGLE_AUTH_URL}?{query}")


@router.get("/google/callback")
async def google_oauth_callback(code: str, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback — exchange code for user info and create/login user."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")

    redirect_uri = f"{settings.OAUTH_REDIRECT_BASE}/api/auth/oauth/google/callback"

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )

    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange OAuth code")

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    # Get user info from Google
    async with httpx.AsyncClient() as client:
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if userinfo_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get user info from Google")

    google_user = userinfo_response.json()
    email = google_user.get("email")
    name = google_user.get("name", email.split("@")[0])
    picture = google_user.get("picture")
    google_id = google_user.get("id")

    if not email:
        raise HTTPException(status_code=400, detail="Could not get email from Google")

    # Find or create user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            name=name,
            avatar_url=picture,
            oauth_provider="google",
            oauth_id=google_id,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
    else:
        # Update OAuth info if needed
        if not user.oauth_provider:
            user.oauth_provider = "google"
            user.oauth_id = google_id
        if picture and not user.avatar_url:
            user.avatar_url = picture

    jwt_token = create_access_token({"sub": user.id, "email": user.email})

    # Redirect to frontend with token
    frontend_url = settings.ALLOWED_ORIGINS.split(",")[0].strip()
    return RedirectResponse(
        url=f"{frontend_url}/auth/callback?token={jwt_token}&name={name}&email={email}"
    )


@router.post("/google/token", response_model=TokenResponse)
async def google_oauth_token(code: str, db: AsyncSession = Depends(get_db)):
    """
    Exchange Google OAuth code for JWT token (for SPA frontend flow).
    Frontend sends the authorization code; backend returns JWT.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")

    redirect_uri = f"{settings.OAUTH_REDIRECT_BASE}/api/auth/oauth/google/callback"

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )

    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange OAuth code")

    access_token = token_response.json().get("access_token")

    async with httpx.AsyncClient() as client:
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    google_user = userinfo_response.json()
    email = google_user.get("email")
    name = google_user.get("name", "")
    picture = google_user.get("picture")
    google_id = google_user.get("id")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            name=name,
            avatar_url=picture,
            oauth_provider="google",
            oauth_id=google_id,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

    jwt_token = create_access_token({"sub": user.id, "email": user.email})
    return TokenResponse(
        access_token=jwt_token,
        user=UserResponse.model_validate(user),
    )
