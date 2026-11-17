"""
LPU GoCart - Authentication & User Pydantic Schemas
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    phone_number: Optional[str] = None
    role: str = Field(default="CUSTOMER")
    
    # Optional metadata
    registration_number: Optional[str] = None
    department: Optional[str] = None
    hostel_block: Optional[str] = None
    license_number: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    full_name: str
    email: str

class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone_number: Optional[str] = None
    role: str
    avatar_url: Optional[str] = None
    registration_number: Optional[str] = None
    department: Optional[str] = None
    hostel_block: Optional[str] = None
    license_number: Optional[str] = None
    assigned_cart_id: Optional[str] = None

    class Config:
        from_attributes = True
