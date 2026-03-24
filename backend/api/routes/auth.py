"""
Auth routes — register, login, OAuth.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from api.core.database import get_db
from api.core.security import hash_password, verify_password, create_access_token
from api.models.models import User
from api.schemas.schemas import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse, UserUpdate,
)
from api.dependencies import get_current_user_from_auth_service
from api.services.otp_service import generate_otp_code, get_otp_expiration, send_otp_email, verify_otp_code, clear_otp

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=body.email,
        name=body.name or body.email.split("@")[0],
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Signup with email/password (alias for register)"""
    # Check if email exists
    result = await db.execute(select(User).where(User.email == body.email))
    existing = result.scalar_one_or_none()
    
    if existing:
        # User already exists (possibly from OTP flow) - update password
        if not existing.hashed_password:  # type: ignore[operator]
            existing.hashed_password = hash_password(body.password)  # type: ignore[assignment]
            if body.name:
                existing.name = body.name  # type: ignore[assignment]
            await db.flush()
            await db.refresh(existing)
            token = create_access_token({"sub": existing.id, "email": existing.email})
            return TokenResponse(
                access_token=token,
                user=UserResponse.model_validate(existing),
            )
        else:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user = User(
        email=body.email,
        name=body.name or body.email.split("@")[0],
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if user has a password (OTP-only users won't have one)
    if not user.hashed_password:  # type: ignore[operator]
        raise HTTPException(status_code=401, detail="This account uses OTP login. Use 'Send OTP' to login.")
    
    # Verify password
    if not verify_password(body.password, user.hashed_password):  # type: ignore[arg-type]
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:  # type: ignore[operator]
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token({"sub": user.id, "email": user.email})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user_from_auth_service)):
    """Get current user profile."""
    return user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdate,
    user: User = Depends(get_current_user_from_auth_service),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile."""
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    await db.flush()
    await db.refresh(user)
    return user


# ── OTP-based Passwordless Login ──────────────────────


class SendOtpRequest(BaseModel):
    email: str


class VerifyOtpRequest(BaseModel):
    email: str
    otp_code: str


class OtpResponse(BaseModel):
    message: str


@router.post("/send-otp", response_model=OtpResponse)
async def send_otp(body: SendOtpRequest, db: AsyncSession = Depends(get_db)):
    """
    Send OTP to user's email.
    If user doesn't exist, create an account automatically.
    """
    email = body.email.lower().strip()
    
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    # Find or create user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Auto-create user on first OTP request
        user = User(
            email=email,
            name=email.split("@")[0],
            hashed_password=None,  # No password for OTP users
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
    
    # Generate and store OTP
    otp_code = generate_otp_code()
    user.otp_code = otp_code  # type: ignore[assignment]
    user.otp_expires_at = get_otp_expiration()  # type: ignore[assignment]
    await db.flush()
    
    # Send OTP via email
    success = await send_otp_email(email, otp_code, user.name)  # type: ignore[arg-type]
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP. Try again later.")
    
    return OtpResponse(
        message=f"OTP sent to {email}. Valid for 10 minutes."
    )


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(body: VerifyOtpRequest, db: AsyncSession = Depends(get_db)):
    """
    Verify OTP and return access token.
    """
    email = body.email.lower().strip()
    otp_code = body.otp_code.strip()
    
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    if not otp_code or len(otp_code) != 6:
        raise HTTPException(status_code=400, detail="Invalid OTP format (must be 6 digits)")
    
    # Find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found. Request OTP first.")
    
    if not user.is_active:  # type: ignore[operator]
        raise HTTPException(status_code=403, detail="Account is disabled")
    
    # Verify OTP
    is_valid, message = verify_otp_code(user.otp_code, user.otp_expires_at, otp_code)  # type: ignore[arg-type]
    
    if not is_valid:
        raise HTTPException(status_code=401, detail=message)
    
    # Clear OTP after successful verification
    clear_otp(user)
    await db.flush()
    
    # Create access token
    token = create_access_token({"sub": user.id, "email": user.email})
    
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )
