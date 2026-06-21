"""ASTRA Authentication Schemas."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: str = Field(default="officer", pattern="^(officer|supervisor|admin)$")
    badge_number: Optional[str] = None
    police_station: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema for user response (no password)."""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    badge_number: Optional[str]
    police_station: Optional[str]
    is_active: bool
    created_at: Optional[datetime]
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class OTPResponse(BaseModel):
    """Response when OTP is required."""
    requires_otp: bool = True
    username: str
    message: str


class OTPVerify(BaseModel):
    """Schema for OTP verification."""
    username: str
    otp: str


class TokenData(BaseModel):
    """Data encoded in the JWT token."""
    user_id: int
    username: str
    role: str
