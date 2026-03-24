"""
FastAPI integration with auth-service (Node.js microservice)
This module handles JWT validation and proxying auth calls from Python to Node.
"""
import os
from typing import Optional
import httpx
import jwt
from fastapi import HTTPException, Header, status

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:4000")
JWT_SECRET = os.getenv("JWT_SECRET", "athena_jwt_secret_key_change_in_prod_2026")
JWT_ALGORITHM = "HS256"


async def get_current_user(authorization: str = Header(None)):
    """JWT validation middleware - extracts and validates Bearer token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization scheme"
            )
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return {"user_id": user_id, "email": email}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed authorization header"
        )


async def proxy_auth_request(method: str, endpoint: str, data: Optional[dict] = None, headers: Optional[dict] = None) -> dict:
    """Proxy request to auth-service"""
    async with httpx.AsyncClient() as client:
        url = f"{AUTH_SERVICE_URL}{endpoint}"
        req_headers = headers or {}
        try:
            if method.upper() == "POST":
                response = await client.post(url, json=data, timeout=10, headers=req_headers)
            else:
                response = await client.get(url, timeout=10, headers=req_headers)
            
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("error", "Auth service error")
                )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Auth service unavailable: {str(e)}"
            )
