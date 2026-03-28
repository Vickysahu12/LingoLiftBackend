from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import random
import resend
from app.account.models import User
from app.schemas.auth import RegisterRequest, LoginRequest, VerifyOTPRequest, ResendOTPRequest
from app.db.security import hash_password, verify_password, create_access_token
from app.db.config import settings

class AuthService:

    def generate_otp(self) -> str:
        return str(random.randint(100000, 999999))

    async def send_otp_email(self, email: str, otp: str, name: str):
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": email,
            "subject": "Your LingoLift OTP Code",
            "html": f"""
                <h2>Hello {name}!</h2>
                <p>Your OTP for LingoLift verification is:</p>
                <h1 style="color:#1F3B1F; letter-spacing:8px;">{otp}</h1>
                <p>Valid for <b>10 minutes</b>.</p>
            """
        })

    async def register(self, data: RegisterRequest, db: AsyncSession):
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        result = await db.execute(select(User).where(User.phone == data.phone))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Phone number already registered")

        otp = self.generate_otp()
        otp_expires = datetime.now(timezone.utc) + timedelta(minutes=10)

        user = User(
            name=data.name,
            phone=data.phone,
            email=data.email,
            hashed_password=hash_password(data.password),
            auth_provider="email",
            is_verified=False,
            otp_code=otp,
            otp_expires_at=otp_expires
        )
        db.add(user)
        await db.flush()

        await self.send_otp_email(data.email, otp, data.name)
        return user

    async def verify_otp(self, data: VerifyOTPRequest, db: AsyncSession):
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_verified:
            raise HTTPException(status_code=400, detail="Email already verified")
        if not user.otp_code or user.otp_code != data.otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        if datetime.now(timezone.utc) > user.otp_expires_at:
            raise HTTPException(status_code=400, detail="OTP expired")

        user.is_verified = True
        user.otp_code = None
        user.otp_expires_at = None
        await db.flush()

        token = create_access_token({"sub": str(user.id)})
        return token, user

    async def resend_otp(self, data: ResendOTPRequest, db: AsyncSession):
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_verified:
            raise HTTPException(status_code=400, detail="Email already verified")

        otp = self.generate_otp()
        user.otp_code = otp
        user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        await db.flush()

        await self.send_otp_email(data.email, otp, user.name)
        return {"message": "OTP sent successfully"}

    async def login(self, data: LoginRequest, db: AsyncSession):
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user or not user.hashed_password:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")
        if not user.is_verified:
            raise HTTPException(status_code=403, detail="Email not verified. Please verify your email first.")

        token = create_access_token({"sub": str(user.id)})
        return token, user

auth_service = AuthService()