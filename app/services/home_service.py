from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date, datetime, timedelta
from app.account.models import User
from app.models.daily_stats import UserDailyStats, UserStreak
from app.models.vocab import VocabProgress
import uuid

class HomeService:

    async def get_home_stats(self, user: User, db: AsyncSession):

        # ── Day count (kitne din se joined) ──
        day_count = (date.today() - user.created_at.date()).days + 1

        # ── Streak ──
        streak_result = await db.execute(
            select(UserStreak).where(UserStreak.user_id == user.id)
        )
        streak_obj   = streak_result.scalar_one_or_none()
        streak       = streak_obj.current_streak if streak_obj else 0
        week_activity = streak_obj.week_activity if streak_obj else [False] * 7

        # ── Today's stats ──
        today = date.today()
        stats_result = await db.execute(
            select(UserDailyStats).where(
                and_(
                    UserDailyStats.user_id == user.id,
                    UserDailyStats.date == today
                )
            )
        )
        today_stats = stats_result.scalar_one_or_none()

        study_minutes   = today_stats.study_minutes   if today_stats else 0
        today_progress  = today_stats.today_progress  if today_stats else 0
        vocab_completed = today_stats.vocab_completed  if today_stats else 0
        rc_passages     = today_stats.rc_passages      if today_stats else 0
        va_questions    = today_stats.va_questions     if today_stats else 0

        # ── Study time format ──
        hours   = study_minutes // 60
        minutes = study_minutes % 60
        if hours > 0:
            study_time = f"{hours}h {minutes}m"
        else:
            study_time = f"{minutes}m"

        return {
            "name":           user.name.split()[0],  # First name only
            "day_count":      day_count,
            "streak":         streak,
            "study_time":     study_time if study_minutes > 0 else "0m",
            "today_progress": today_progress,
            "practice_stats": {
                "vocab":   {"done": vocab_completed, "total": 20},
                "rc":      {"passages": rc_passages},
                "va":      {"types": "PJ • OOO"},
            },
            "test_stats": {
                "rc":  {"label": "Not attempted"},
                "va":  {"label": "Not attempted"},
            },
            "week_activity": week_activity,
        }

    async def get_practice_modules(self, user_id: uuid.UUID, db: AsyncSession):
        # Vocab progress
        from sqlalchemy import func
        from app.models.vocab import VocabWord, VocabProgress

        total_vocab = await db.execute(
            select(func.count()).select_from(VocabWord).where(VocabWord.is_active == True)
        )
        completed_vocab = await db.execute(
            select(func.count()).select_from(VocabProgress).where(
                and_(VocabProgress.user_id == user_id, VocabProgress.is_completed == True)
            )
        )
        total   = total_vocab.scalar() or 1
        done    = completed_vocab.scalar() or 0
        vocab_pct = round((done / total) * 100)

        # Today's stats
        today_result = await db.execute(
            select(UserDailyStats).where(
                and_(
                    UserDailyStats.user_id == user_id,
                    UserDailyStats.date == date.today()
                )
            )
        )
        today = today_result.scalar_one_or_none()
        goal_completed = (today.vocab_completed if today else 0)

        modules = [
            {
                "id":          "vocab",
                "title":       "VOCAB",
                "description": f"Master 500+ high-frequency CAT words. {done}/{total} completed.",
                "progress":    vocab_pct,
                "tag":         "HIGH PRIORITY" if vocab_pct < 50 else None,
            },
            {
                "id":          "rc",
                "title":       "RC",
                "description": "Reading Comprehension passages with detailed analysis.",
                "progress":    0,
                "tag":         "NEW CONTENT",
            },
            {
                "id":          "essay",
                "title":       "ESSAY / ARTICLE",
                "description": "Daily editorial analysis from The Guardian and AEON.",
                "progress":    0,
                "tag":         None,
            },
            {
                "id":          "va",
                "title":       "VERBAL ABILITY",
                "description": "Parajumbles, Odd One Out, and Critical Reasoning drills.",
                "progress":    0,
                "tag":         None,
            },
        ]

        return {
            "modules":        modules,
            "goal_completed": goal_completed,
            "goal_total":     20,
            "streak":         0,
        }

home_service = HomeService()