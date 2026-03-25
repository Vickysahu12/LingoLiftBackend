from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException, UploadFile
import uuid

from app.account.models import User
from app.models.mock import TestAttempt, AttemptStatus
from app.schemas.profile import UpdateProfileRequest


class ProfileService:

    # ── GET /user/profile ─────────────────────────────────────────────────────
    async def get_profile(self, user_id: uuid.UUID, db: AsyncSession):
        # Fetch user
        result = await db.execute(select(User).where(User.id == user_id))
        user   = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Compute stats from TestAttempt table
        stats = await self._compute_stats(user_id, db)

        return {
            "id":          user.id,
            "name":        user.name,
            "email":       user.email,
            "phone":       user.phone,
            "avatar_url":  user.profile_pic,
            "target_exam": user.target_exam,
            "target_year": user.target_year,
            "stats":       stats,
            # Subscription — v2 mein real table se aayega, abhi placeholder
            "subscription": {
                "plan":       "Free",
                "expires_at": None,
                "is_active":  False,
            },
        }

    # ── PUT /user/profile ─────────────────────────────────────────────────────
    async def update_profile(
        self,
        user_id: uuid.UUID,
        data: UpdateProfileRequest,
        db: AsyncSession,
    ):
        result = await db.execute(select(User).where(User.id == user_id))
        user   = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check phone uniqueness if being updated
        if data.phone and data.phone != user.phone:
            existing = await db.execute(
                select(User).where(
                    and_(User.phone == data.phone, User.id != user_id)
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Phone number already in use")

        # Apply updates (only fields that were provided)
        if data.name        is not None: user.name        = data.name
        if data.phone       is not None: user.phone       = data.phone
        if data.target_exam is not None: user.target_exam = data.target_exam
        if data.target_year is not None: user.target_year = data.target_year

        await db.flush()
        return {
            "success":     True,
            "name":        user.name,
            "phone":       user.phone,
            "target_exam": user.target_exam,
            "target_year": user.target_year,
        }

    # ── PUT /user/avatar ──────────────────────────────────────────────────────
    # Placeholder — v2 mein S3/Cloudinary upload hoga
    async def update_avatar(
        self,
        user_id: uuid.UUID,
        avatar_url: str,          # v2: UploadFile → upload → return CDN URL
        db: AsyncSession,
    ):
        result = await db.execute(select(User).where(User.id == user_id))
        user   = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.profile_pic = avatar_url
        await db.flush()
        return {"success": True, "avatar_url": avatar_url}

    # ── PRIVATE: Compute stats from TestAttempt ───────────────────────────────
    async def _compute_stats(self, user_id: uuid.UUID, db: AsyncSession) -> dict:
        """
        Computes all 4 stats dynamically from TestAttempt table.
        No extra columns needed on User.
        """
        # Total submitted attempts
        attempts_res = await db.execute(
            select(TestAttempt).where(
                and_(
                    TestAttempt.user_id == user_id,
                    TestAttempt.status  == AttemptStatus.submitted,
                )
            )
        )
        attempts = attempts_res.scalars().all()

        tests_given = len(attempts)

        # Avg score (as percentage of max_score)
        avg_score = 0.0
        if tests_given > 0:
            valid = [a for a in attempts if a.max_score > 0]
            if valid:
                avg_score = round(
                    sum((a.score / a.max_score) * 100 for a in valid) / len(valid), 1
                )

        # Rank — count users with higher avg score than this user
        # Simple approach: count users with more submitted attempts (proxy for rank)
        # v2 mein: leaderboard table se real rank aayega
        rank_res = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        total_users = rank_res.scalar() or 1
        # Placeholder rank until leaderboard is built
        rank = max(1, int(total_users * (1 - avg_score / 100))) if avg_score > 0 else total_users

        return {
            "streak":      0,          # current_streak field from User model (updated by activity)
            "tests_given": tests_given,
            "avg_score":   avg_score,
            "rank":        rank,
        }


profile_service = ProfileService()