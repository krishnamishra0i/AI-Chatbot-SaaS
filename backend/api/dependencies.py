"""
Auth dependency — extracts and validates JWT bearer token.
Supports both backend-generated JWTs and auth-service JWTs.
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
    except Exception as e:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency: returns the authenticated User or raises 401.
    Tries multiple auth methods:
    1. Backend JWT from HTTPBearer
    2. Auth-service JWT from Authorization header
    3. Database user lookup
    """
    user_id = None
    
    # Method 1: Try HTTPBearer (old system)
    if credentials:
        try:
            payload = decode_access_token(credentials.credentials)
            user_id = payload.get("sub")
        except Exception:
            pass
    
    # Method 2: Try auth-service JWT format
    if not user_id:
        try:
            # Get token from credentials or re-use from request context
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        except HTTPException:
            raise
        except Exception:
            pass
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
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
    Supports multiple auth providers: auth-service, otp-mongodb, etc.
    """
    # Look up by oauth_id + provider
    result = await db.execute(
        select(User).where(
            (User.oauth_id == user_id) & (User.oauth_provider == provider)
        )
    )
    user = result.scalar_one_or_none()
    
    if user:
        return user
    
    # If email is provided, check if user exists with that email (from another auth provider)
    if email:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # Update the oauth credentials for this provider
            existing_user.oauth_id = user_id  # type: ignore[assignment]
            existing_user.oauth_provider = provider  # type: ignore[assignment]
            await db.flush()
            await db.refresh(existing_user)
            print(f"[UPDATE] User oauth credentials updated: email={email}, new_oauth_id={user_id}, provider={provider}")
            return existing_user
    
    # Create new user
    import uuid
    
    new_user = User(
        id=str(uuid.uuid4()),
        email=email or f"user_{user_id}@{provider}.local",
        oauth_id=user_id,
        oauth_provider=provider,
        is_active=True,
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    print(f"[CREATE] New user created: id={new_user.id}, oauth_id={user_id}, provider={provider}, email={email}")
    return new_user


async def get_current_user_from_auth_service(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get User from JWT in Authorization header. (backend auth, auth-service, or OTP)
    Supports:
    1. Auth-service JWTs (with oauth_id in 'sub')
    2. Backend local auth JWTs (with user.id in 'sub')
    3. OTP system JWTs (with mongodb user_id in 'sub', email in payload)
    
    Returns the User object. Auto-creates user if from OTP/auth-service.
    """
    print("\n[TRACE] get_current_user_from_auth_service called")
    print(f"[TRACE] authorization header: {authorization[:30] if authorization else 'NONE'}...")
    
    if not authorization:
        print("[TRACE] No authorization header")
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
        # Decode with JWT_SECRET (works for OTP, auth-service, and backend JWTs)
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=['HS256']
        )
        
        user_id = payload.get('sub')
        email = payload.get('email')
        
        print(f"[TRACE] Token decoded - sub: {user_id}, email: {email}")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        # Try to find user by id first (backend local auth)
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"[TRACE] Found user by id: {user.id}")
            return user
        
        # Try to find user by oauth_id (auth-service)
        result = await db.execute(
            select(User).where(
                (User.oauth_id == user_id) & (User.oauth_provider == "auth-service")
            )
        )
        user = result.scalar_one_or_none()
        
        if user:
            print(f"[TRACE] Found user by oauth_id: {user.id}")
            return user
        
        # Auto-create user if coming from auth-service or OTP
        # Detect if it's an OTP user (mongodb ObjectId format) or auth-service
        provider = "auth-service"
        if len(str(user_id)) == 24:  # MongoDB ObjectId is 24 chars
            provider = "otp-mongodb"
        
        print(f"[TRACE] Auto-creating user for provider: {provider}")
        user = await ensure_user_exists(db, user_id, email, provider)
        print(f"[TRACE] User auto-created: {user.id}")
        return user
        
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
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print("[ERROR] get_current_user_from_auth_service failed:")
        print(f"[ERROR] {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
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
