"""
MongoDB-based user schema for OTP-only authentication
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import model_validator

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)


class UserModel(BaseModel):
    """User model for MongoDB - OTP only (no password)"""
    id: Optional[PyObjectId] = Field(alias="_id")
    email: str = Field(..., unique=True, index=True)
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # OTP fields
    otp_code: Optional[str] = None
    otp_expires_at: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    is_verified: bool = False  # Set to True after first OTP verification
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class SendOTPRequest(BaseModel):
    email: str = Field(..., description="User email address")


class VerifyOTPRequest(BaseModel):
    email: str = Field(..., description="User email address")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")

    @model_validator(mode="before")
    @classmethod
    def map_otp_alias(cls, data):
        # Backward compatibility: accept both `otp_code` and `otp` payload keys.
        if isinstance(data, dict) and "otp_code" not in data and "otp" in data:
            data["otp_code"] = data["otp"]
        return data


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class OTPResponse(BaseModel):
    message: str
    status: str = "success"
