from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime, timedelta, timezone
import random
import resend
from app.account.models import User
from app.schemas.auth import RegisterRequest, LoginRequest, GoogleAuthRequest, VerifyOTPRequest, ResendOTPRequest
from app.db.security import hash_password, verify_password, create_access_token
from app.db.config import settings

resend.api_key = settings.RESEND_API_KEY

class AuthService:

    # ─── OTP Generate ─────────────────────────────────────────
    def generate_otp(self) -> str:
        return str(random.randint(100000, 999999))

    # ─── OTP Email Bhejo ──────────────────────────────────────
    async def send_otp_email(self, email: str, otp: str, name: str):
        try:
            resend.Emails.send({
                "from": "Verbify <onboarding@resend.dev>",
                "to": email,
                "subject": "Your Verbify OTP Code",
                "html": f"""
                    <h2>Hello {name}!</h2>
                    <p>Your OTP for LingoLift verification is:</p>
                    <h1 style="color:#1F3B1F; letter-spacing:8px;">{otp}</h1>
                    <p>This OTP is valid for <b>10 minutes</b>.</p>
                    <p>If you didn't request this, ignore this email.</p>
                """
            })
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP email"
            )

    # ─── Email Register ───────────────────────────────────────
    async def register(self, data: RegisterRequest, db: AsyncSession):
        # Email already exists?
        result = await db.execute(select(User).where(User.email == data.email))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Phone already exists?
        result = await db.execute(select(User).where(User.phone == data.phone))
        existing_phone = result.scalar_one_or_none()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

        # OTP generate karo
        otp = self.generate_otp()
        otp_expires = datetime.now(timezone.utc) + timedelta(minutes=10)

        # New user banao
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

        # OTP email bhejo
        await self.send_otp_email(data.email, otp, data.name)

        return user

    # ─── OTP Verify ───────────────────────────────────────────
    async def verify_otp(self, data: VerifyOTPRequest, db: AsyncSession):
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )

        if not user.otp_code or user.otp_code != data.otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )

        if datetime.now(timezone.utc) > user.otp_expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP expired"
            )

        # Verified kar do
        user.is_verified = True
        user.otp_code = None
        user.otp_expires_at = None
        await db.flush()

        token = create_access_token({"sub": str(user.id)})
        return token, user

    # ─── OTP Resend ───────────────────────────────────────────
    async def resend_otp(self, data: ResendOTPRequest, db: AsyncSession):
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )

        otp = self.generate_otp()
        user.otp_code = otp
        user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        await db.flush()

        await self.send_otp_email(data.email, otp, user.name)
        return {"message": "OTP sent successfully"}

    # ─── Email Login ──────────────────────────────────────────
    async def login(self, data: LoginRequest, db: AsyncSession):
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        # ⚠️ Verified nahi hai toh block karo
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Please verify your email first."
            )

        token = create_access_token({"sub": str(user.id)})
        return token, user

    # ─── Google OAuth ─────────────────────────────────────────
    async def google_auth(self, data: GoogleAuthRequest, db: AsyncSession):
        try:
            google_data = id_token.verify_oauth2_token(
                data.id_token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )

        google_id = google_data["sub"]
        email = google_data["email"]
        name = google_data.get("name", "")
        picture = google_data.get("picture", "")

        result = await db.execute(select(User).where(User.google_id == google_id))
        user = result.scalar_one_or_none()

        if not user:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

            if user:
                user.google_id = google_id
                user.profile_pic = picture
                user.auth_provider = "both"
                user.is_verified = True  # Google verified email hai
            else:
                user = User(
                    google_id=google_id,
                    email=email,
                    name=name,
                    profile_pic=picture,
                    auth_provider="google",
                    is_verified=True  # Google verified email hai
                )
                db.add(user)

        await db.flush()
        token = create_access_token({"sub": str(user.id)})
        return token, user

auth_service = AuthService()