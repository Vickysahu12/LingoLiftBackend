# app/services/streak_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, timedelta
from app.models.daily_stats import UserStreak
import uuid

async def update_streak(user_id: uuid.UUID, db: AsyncSession):
    today = date.today()

    result = await db.execute(
        select(UserStreak).where(UserStreak.user_id == user_id)
    )
    streak = result.scalar_one_or_none()

    if not streak:
        streak = UserStreak(
            user_id=user_id,
            current_streak=1,
            longest_streak=1,
            last_active_date=today,
            week_activity=[False] * 7
        )
        db.add(streak)
    else:
        # Aaj already update ho chuka hai
        if streak.last_active_date == today:
            return streak

        if streak.last_active_date == today - timedelta(days=1):
            streak.current_streak += 1  # Consecutive day
        else:
            streak.current_streak = 1   # Streak toot gayi

        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.last_active_date = today

    # ⚠️ JSON mutation — reassign karna ZARURI hai
    activity = list(streak.week_activity or [False] * 7)
    activity[today.weekday()] = True  # 0=Mon, 6=Sun
    streak.week_activity = activity

    await db.commit()
    await db.refresh(streak)
    return streak