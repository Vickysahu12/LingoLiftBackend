from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class RegisterRequest(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthRequest(BaseModel):
    id_token: str

# OTP ke liye ← YE 2 ADD KARO
class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class ResendOTPRequest(BaseModel):
    email: EmailStr

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    phone: Optional[str] = None
    profile_pic: Optional[str] = None
    is_admin: bool
    is_verified: bool          # ← YE BHI ADD KARO
    auth_provider: str

    model_config = {"from_attributes": True}

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse