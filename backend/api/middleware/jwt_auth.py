"""
Auth middleware — Extract user from JWT token
"""
from fastapi import Depends, HTTPException, Header
import jwt
from api.core.config import get_settings

settings = get_settings()

def verify_jwt_token(authorization: str = Header(None)):
    """
    Extract and verify JWT token from Authorization header
    Returns: dict with user info (userId, email, ...)
    """
    if not authorization:
        return None
    
    try:
        # Extract token from "Bearer <token>"
        if not authorization.startswith('Bearer '):
            return None
        
        token = authorization.split(' ', 1)[1]
        
        # Decode JWT
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=['HS256']
        )
        
        # JWT from auth-service uses 'sub' for user ID
        return {
            'user_id': str(payload.get('sub')),
            'email': payload.get('email'),
            'iat': payload.get('iat'),
            'exp': payload.get('exp'),
        }
    except Exception as e:
        print(f"JWT verification failed: {e}")
        return None

def get_current_user_from_jwt(authorization: str = Header(None)):
    """
    Dependency for protected routes
    Raises 401 if token is invalid
    """
    user = verify_jwt_token(authorization)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing authentication token"
        )
    return user

def get_optional_user_from_jwt(authorization: str = Header(None)):
    """
    Optional JWT verification - returns user if valid, None otherwise
    Used for routes that work with or without auth
    """
    return verify_jwt_token(authorization)
