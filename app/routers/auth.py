from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, GoogleAuthRequest,
    AuthResponse, UserResponse, VerifyOTPRequest, ResendOTPRequest
)
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.register(data, db)
    return {"message": "OTP sent to your email. Please verify.", "email": user.email}

@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(data: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    token, user = await auth_service.verify_otp(data, db)
    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))

@router.post("/resend-otp")
async def resend_otp(data: ResendOTPRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.resend_otp(data, db)

@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    token, user = await auth_service.login(data, db)
    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))

@router.post("/google", response_model=AuthResponse)
async def google_login(data: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    token, user = await auth_service.google_auth(data, db)
    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))