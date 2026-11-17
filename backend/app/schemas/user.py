"""
LPU GoCart - User Schemas
Roles: ADMIN, DRIVER, CUSTOMER
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    phone_number: Optional[str] = None
    role: str = Field(default="CUSTOMER", pattern="^(ADMIN|DRIVER|CUSTOMER)$")

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

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone_number: Optional[str] = None
    role: str
    is_active: bool

    class Config:
        from_attributes = True
