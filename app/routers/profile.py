from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.dependencies import get_current_user
from app.account.models import User
from app.schemas.profile import (
    ProfileResponse,
    UpdateProfileRequest,
    UpdateProfileResponse,
)
from app.services.profile_service import profile_service

router = APIRouter(prefix="/user", tags=["Profile"])


# ── GET /user/profile ─────────────────────────────────────────────────────────
# ProfileScreen.jsx → fetches on mount (replaces MOCK_USER)
# Returns: id, name, email, phone, avatar_url, target_exam, target_year,
#          stats{streak, tests_given, avg_score, rank}, subscription{plan, ...}

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User       = Depends(get_current_user),
    db: AsyncSession         = Depends(get_db),
):
    return await profile_service.get_profile(current_user.id, db)


# ── PUT /user/profile ─────────────────────────────────────────────────────────
# EditProfile screen (coming in v2) → update name, phone, target_exam, target_year

@router.put("/profile", response_model=UpdateProfileResponse)
async def update_profile(
    data: UpdateProfileRequest,
    current_user: User   = Depends(get_current_user),
    db: AsyncSession     = Depends(get_db),
):
    return await profile_service.update_profile(current_user.id, data, db)


# ── PUT /user/avatar ──────────────────────────────────────────────────────────
# ProfileScreen camera button → v2 mein S3 upload hoga
# Abhi ke liye: frontend sends avatar_url string directly

@router.put("/avatar")
async def update_avatar(
    avatar_url: str,
    current_user: User   = Depends(get_current_user),
    db: AsyncSession     = Depends(get_db),
):
    return await profile_service.update_avatar(current_user.id, avatar_url, db)