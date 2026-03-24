"""
JWT token creation, verification, password hashing.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
import secrets

from api.core.config import get_settings

settings = get_settings()


# ── Password Hashing ────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── JWT Tokens ──────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    # Use JWT_SECRET so tokens are compatible with auth-service and frontend validation
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    # Use JWT_SECRET to match token creation and auth-service standard
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


# ── API Key Generation ──────────────────────────────

def generate_api_key() -> str:
    """Generate a secure random API key: ak_<48-char hex>"""
    return f"ak_{secrets.token_hex(24)}"
