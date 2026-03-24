"""
Passwordless OTP Authentication Routes for MongoDB
- No passwords
- No signup/login endpoints
- Simple 2-step OTP flow: send OTP → verify OTP
"""

from fastapi import APIRouter, HTTPException, Header
from datetime import datetime, timezone

from api.core.mongodb import get_db
from api.core.security import create_access_token
from api.schemas.otp_schemas import (
    SendOTPRequest, VerifyOTPRequest, TokenResponse, OTPResponse
)
from api.services.otp_mongodb_service import (
    generate_otp_code, get_otp_expiration, send_otp_email, 
    verify_otp_code
)

router = APIRouter(prefix="/api/auth/otp", tags=["OTP Authentication"])


@router.post("/send", response_model=OTPResponse)
async def send_otp(body: SendOTPRequest):
    """
    Passwordless Authentication - Step 1: Send OTP
    
    For both new and existing users:
    - New user? Create account with OTP
    - Existing user? Send OTP to reset/login
    
    Response: OTP sent to email
    """
    db = get_db()
    email = body.email.lower().strip()
    
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    try:
        # Check if user exists
        user = await db.users.find_one({"email": email})  # type: ignore[union-attr]
        
        if not user:
            # New user - create account with OTP
            user = {
                "email": email,
                "name": email.split("@")[0],
                "is_active": False,  # Not active until first OTP verification
                "is_verified": False,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            result = await db.users.insert_one(user)  # type: ignore[union-attr]
            user["_id"] = result.inserted_id
            print(f"[OTP] ✓ New user created: {email}")
        
        # Generate OTP (always generate new one)
        otp_code = generate_otp_code()
        otp_expires_at = get_otp_expiration()
        
        # Store OTP in database
        await db.users.update_one(  # type: ignore[union-attr]
            {"email": email},
            {
                "$set": {
                    "otp_code": otp_code,
                    "otp_expires_at": otp_expires_at,
                    "updated_at": datetime.now(timezone.utc),
                }
            }
        )
        
        # Send OTP via email
        name = user.get("name", email.split("@")[0])
        success = await send_otp_email(email, otp_code, name)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send OTP. Try again later.")
        
        return OTPResponse(
            message=f"OTP sent to {email}. Valid for 10 minutes.",
            status="success"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[OTP] ✗ Send OTP error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.post("/verify", response_model=TokenResponse)
async def verify_otp(body: VerifyOTPRequest):
    """
    Passwordless Authentication - Step 2: Verify OTP & Login
    
    Validates OTP and returns JWT token for authentication
    
    Response: JWT token + user info
    """
    db = get_db()
    email = body.email.lower().strip()
    otp_code = body.otp_code.strip()
    
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    if not otp_code or len(otp_code) != 6:
        raise HTTPException(status_code=400, detail="Invalid OTP format (must be 6 digits)")
    
    try:
        # Find user
        user = await db.users.find_one({"email": email})  # type: ignore[union-attr]
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found. Send OTP first.")
        
        # Verify OTP
        is_valid, message = verify_otp_code(
            user.get("otp_code"),
            user.get("otp_expires_at"),
            otp_code
        )
        
        if not is_valid:
            raise HTTPException(status_code=401, detail=message)
        
        # Mark user as verified and active
        update_data = {
            "is_active": True,
            "is_verified": True,
            "last_login": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "otp_code": None,  # Clear OTP
            "otp_expires_at": None,
        }
        
        result = await db.users.find_one_and_update(  # type: ignore[union-attr]
            {"email": email},
            {"$set": update_data},
            return_document=True
        )
        
        # Create JWT token
        user_id = str(result["_id"])
        token = create_access_token({"sub": user_id, "email": email})
        
        # Return user info without sensitive fields
        user_response = {
            "id": user_id,
            "email": result["email"],
            "name": result.get("name"),
            "avatar_url": result.get("avatar_url"),
            "is_verified": result.get("is_verified"),
        }
        
        print(f"[OTP] ✓ User verified and logged in: {email}")
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[OTP] ✗ Verify OTP error: {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/me")
async def get_me(authorization: str = Header(None)):
    """
    Get current user profile (requires valid JWT token)
    Protected endpoint that validates Bearer token
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    
    try:
        from api.core.security import decode_access_token
        token = authorization.replace("Bearer ", "")
        payload = decode_access_token(token)
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: no user id"
            )
        
        # Fetch user from database to get current info
        db = get_db()
        user = await db.users.find_one({"email": email})  # type: ignore[union-attr]
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user.get("name"),
            "avatar_url": user.get("avatar_url"),
            "is_verified": user.get("is_verified", False),
            "is_active": user.get("is_active", False),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[OTP] ✗ /me endpoint error: {e}")
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )
