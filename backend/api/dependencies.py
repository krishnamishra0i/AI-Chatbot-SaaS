"""
Auth dependency — extracts and validates JWT bearer token.
Supports both backend-generated JWTs and auth-service JWTs.

WHICH DEPENDENCY TO USE IN YOUR ROUTES:
======================================

1. **For protected endpoints that need User object:**
   Use: `get_current_user_from_auth_service`
   
   @router.get("/me")
   async def get_me(user: User = Depends(get_current_user_from_auth_service)):
       return user

2. **For endpoints that work without database lookup:**
   Use: `get_current_user_from_jwt_header`
   
   @router.post("/validate")
   async def validate_token(payload: dict = Depends(get_current_user_from_jwt_header)):
       return payload

3. **For endpoints where auth is optional:**
   Use: `get_optional_user`
   
   @router.get("/public")
   async def get_public(user: Optional[User] = Depends(get_optional_user)):
       return {"user": user}

DEPRECATED:
- `get_current_user` - Use `get_current_user_from_auth_service` instead
- `get_current_user_jwt_from_header` - Use `get_current_user_from_jwt_header` instead

JWT FLOW:
=========
1. Frontend sends Authorization: Bearer <JWT>
2. Backend validates JWT signature using settings.JWT_SECRET
3. User is looked up in database by ID or oauth_id
4. If not found and from external provider, auto-create user
"""


from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import jwt

from api.core.security import decode_access_token
from api.core.config import get_settings
from api.core.database import get_db
from api.models.models import User

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_jwt_from_header(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> Optional[dict]:
    """
    Extract user info from JWT token in Authorization header.
    Works with both backend JWTs and auth-service JWTs.
    Returns dict with user_id and email.
    """
    if not authorization:
        return None
    
    try:
        # Extract token from "Bearer <token>"
        if not authorization.startswith('Bearer '):
            return None
        
        token = authorization.split(' ', 1)[1]
        
        # Try decoding with JWT_SECRET first (auth-service JWTs)
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=['HS256']
            )
            # Auth-service JWTs use 'sub' for user ID
            return {
                'user_id': str(payload.get('sub')),
                'email': payload.get('email'),
                'source': 'auth-service'
            }
        except jwt.InvalidTokenError:
            # Fallback to backend's old JWT system (SECRET_KEY)
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return {
                'user_id': str(payload.get('sub')),
                'email': payload.get('email'),
                'source': 'backend'
            }
    except Exception:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    DEPRECATED: Use get_current_user_from_auth_service instead.
    This function has been kept for backward compatibility only.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing credentials"
        )
    
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        # Look up user in database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user is None or not user.is_active:  # type: ignore[union-attr]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )


async def get_current_user_from_jwt_header(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    NEW: Extract user from JWT in Authorization header.
    Supports auth-service JWTs with 'sub' claim for user_id.
    Returns dict with user_id, email (doesn't require DB User).
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )
    
    if not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format"
        )
    
    token = authorization.split(' ', 1)[1]
    
    try:
        # Decode with JWT_SECRET (auth-service standard)
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=['HS256']
        )
        
        user_id = payload.get('sub')
        email = payload.get('email')
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        return {
            'user_id': str(user_id),
            'email': email or 'unknown',
            'iat': payload.get('iat'),
            'exp': payload.get('exp'),
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )


async def ensure_user_exists(
    db: AsyncSession,
    user_id: str,
    email: Optional[str] = None,
    provider: str = "auth-service",
) -> User:
    """
    Ensure a User record exists for the given oauth_id.
    Creates one if it doesn't exist.
    Supports multiple auth providers: auth-service, otp-mongodb, google, github, etc.
    
    Returns existing or newly created User.
    Raises HTTPException if user cannot be created.
    """
    if not user_id:
        raise ValueError("user_id cannot be empty")
    
    # ─── Look up by oauth_id + provider ───
    result = await db.execute(
        select(User).where(
            (User.oauth_id == user_id) & (User.oauth_provider == provider)
        )
    )
    user = result.scalar_one_or_none()
    
    if user:
        return user
    
    # ─── Check if email already exists (link new provider to existing account) ───
    if email:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # Link this new oauth provider to existing account
            existing_user.oauth_id = user_id  # type: ignore[assignment]
            existing_user.oauth_provider = provider  # type: ignore[assignment]
            await db.flush()
            await db.refresh(existing_user)
            print(f"[AUTH] Linked provider - email={email}, oauth_provider={provider}")
            return existing_user
    
    # ─── Create new user ───
    import uuid
    
    new_user = User(
        id=str(uuid.uuid4()),
        email=email or f"user_{user_id}@{provider}.local",
        oauth_id=user_id,
        oauth_provider=provider,
        is_active=True,
    )
    db.add(new_user)
    
    try:
        await db.flush()
        await db.refresh(new_user)
        print(f"[AUTH] User created - id={new_user.id}, email={new_user.email}, provider={provider}")
        return new_user
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Failed to create user: {str(e)}")


async def get_current_user_from_auth_service(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    PRIMARY AUTH DEPENDENCY - Get User from JWT in Authorization header.
    
    Supports:
    1. Auth-service JWTs (with oauth_id in 'sub')
    2. Backend local auth JWTs (with user.id in 'sub')
    3. OTP system JWTs (with mongodb user_id in 'sub', email in payload)
    
    Returns the User object. Auto-creates user if from OTP/auth-service.
    
    Raises:
    - 401 if token is missing, invalid, or expired
    - 401 if user not found and cannot be auto-created
    """
    
    # ─── STEP 1: Validate Authorization Header ───
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )
    
    if not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization format. Use: Bearer <token>"
        )
    
    token = authorization.split(' ', 1)[1]
    
    # ─── STEP 2: Decode JWT ───
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=['HS256']
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )
    
    # ─── STEP 3: Extract User ID from Token ───
    user_id = payload.get('sub')
    email = payload.get('email')
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID (sub claim)"
        )
    
    # ─── STEP 4: Find User in Database ───
    
    # Try Method A: Find by primary ID (backend local auth)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user and user.is_active:  # type: ignore[union-attr]
        return user
    elif user and not user.is_active:  # type: ignore[union-attr]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Try Method B: Find by oauth_id (auth-service/external)
    result = await db.execute(
        select(User).where(
            (User.oauth_id == user_id) & (User.oauth_provider.in_(["auth-service", "otp-mongodb", "google", "github"]))
        )
    )
    user = result.scalar_one_or_none()
    
    if user and user.is_active:  # type: ignore[union-attr]
        return user
    elif user and not user.is_active:  # type: ignore[union-attr]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # ─── STEP 5: Auto-create User if from External Provider ───
    try:
        provider = "auth-service"
        if len(str(user_id)) == 24:  # MongoDB ObjectId is 24 chars
            provider = "otp-mongodb"
        
        user = await ensure_user_exists(db, user_id, email, provider)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not create user: {str(e)}"
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Dependency: returns User if authenticated, None otherwise."""
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
