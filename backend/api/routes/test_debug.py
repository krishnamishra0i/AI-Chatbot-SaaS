"""
Test endpoint to debug token verification outside of dependency injection.
"""

from fastapi import APIRouter, Header, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jwt

from api.core.database import get_db
from api.core.config import get_settings
from api.models.models import User

router = APIRouter(prefix="/api/test", tags=["Test"])
settings = get_settings()


@router.get("/token-verify")
async def test_token_verify(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Manual token verification - debug version.
    """
    print(f"\n[TEST] /test/token-verify called")
    print(f"[TEST] Authorization header: {authorization[:50] if authorization else 'NONE'}...")
    
    if not authorization:
        print(f"[TEST] FAILED: No authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )
    
    if not authorization.startswith('Bearer '):
        print(f"[TEST] FAILED: Invalid header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format"
        )
    
    token = authorization.split(' ', 1)[1]
    print(f"[TEST] Token: {token[:50]}...")
    
    try:
        print(f"[TEST] Attempting to decode with JWT_SECRET...")
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=['HS256']
        )
        print(f"[TEST] ✓ Token decoded: sub={payload.get('sub')}")
        
        user_id = payload.get('sub')
        email = payload.get('email')
        
        if not user_id:
            print(f"[TEST] FAILED: No user_id in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        print(f"[TEST] Looking up user by id: {user_id}")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        print(f"[TEST] User lookup result: {user}")
        
        if user:
            print(f"[TEST] ✓ Found user: {user.email}")
            return {
                "status": "success",
                "message": "Token verified",
                "user": {"id": str(user.id), "email": user.email},
                "logs": "All steps succeeded"
            }
        else:
            print(f"[TEST] User not found in database")
            return {
                "status": "warning",
                "message": "Token valid but user not in DB",
                "user_id_from_token": user_id,
                "email_from_token": email
            }
        
    except Exception as e:
        import traceback
        print(f"[TEST] ✗ EXCEPTION: {str(e)}")
        print(f"[TEST] {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )
