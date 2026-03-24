"""
Auth proxy routes for FastAPI
Routes that forward auth requests to the Node.js microservice
"""
from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel, EmailStr
from ..integrations.auth_service import proxy_auth_request, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class OTPRequest(BaseModel):
    email: EmailStr
    otp: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ResendOTPRequest(BaseModel):
    email: EmailStr


class RefreshTokenRequest(BaseModel):
    refreshToken: str = None


@router.post("/signup")
async def signup(req: SignupRequest):
    """Sign up new user - proxied to auth-service"""
    return await proxy_auth_request("POST", "/auth/signup", {
        "name": req.name,
        "email": req.email,
        "password": req.password
    })


@router.post("/verify-otp")
async def verify_otp(req: OTPRequest):
    """Verify OTP - proxied to auth-service"""
    return await proxy_auth_request("POST", "/auth/verify-otp", {
        "email": req.email,
        "otp": req.otp
    })


@router.post("/resend-otp")
async def resend_otp(req: ResendOTPRequest):
    """Resend OTP - proxied to auth-service"""
    return await proxy_auth_request("POST", "/auth/resend-otp", {
        "email": req.email
    })


@router.post("/login")
async def login(req: LoginRequest):
    """Login user - proxied to auth-service"""
    return await proxy_auth_request("POST", "/auth/login", {
        "email": req.email,
        "password": req.password
    })


@router.post("/send-login-otp")
async def send_login_otp(req: ResendOTPRequest):
    """Send OTP for login - proxied to auth-service"""
    return await proxy_auth_request("POST", "/auth/send-login-otp", {
        "email": req.email
    })


@router.post("/verify-login-otp")
async def verify_login_otp(req: OTPRequest):
    """Verify OTP for login - proxied to auth-service"""
    return await proxy_auth_request("POST", "/auth/verify-login-otp", {
        "email": req.email,
        "otp": req.otp
    })


@router.post("/refresh")
async def refresh_token(req: RefreshTokenRequest):
    """Refresh access token - proxied to auth-service"""
    return await proxy_auth_request("POST", "/auth/refresh", {
        "refreshToken": req.refreshToken
    })


@router.post("/logout")
async def logout():
    """Logout user"""
    return await proxy_auth_request("POST", "/auth/logout", {})


@router.get("/me")
async def get_me(authorization: str = Header(None)):
    """Get current user profile (requires valid JWT)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    return await proxy_auth_request("GET", "/auth/me", None, headers={"Authorization": authorization})
