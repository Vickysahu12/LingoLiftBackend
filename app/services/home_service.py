from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import date
from app.account.models import User
from app.models.daily_stats import UserDailyStats, UserStreak
import uuid

class HomeService:

    async def get_home_stats(self, user: User, db: AsyncSession):

        # ── Day count ──────────────────────────────────────────────────────
        day_count = (date.today() - user.created_at.date()).days + 1

        # ── Streak ─────────────────────────────────────────────────────────
        streak_result = await db.execute(
            select(UserStreak).where(UserStreak.user_id == user.id)
        )
        streak_obj    = streak_result.scalar_one_or_none()
        streak        = streak_obj.current_streak if streak_obj else 0
        week_activity = streak_obj.week_activity  if streak_obj else [False] * 7

        # ── Today's stats ──────────────────────────────────────────────────
        today = date.today()
        stats_result = await db.execute(
            select(UserDailyStats).where(
                and_(
                    UserDailyStats.user_id == user.id,
                    UserDailyStats.date    == today
                )
            )
        )
        today_stats = stats_result.scalar_one_or_none()

        study_minutes   = today_stats.study_minutes   if today_stats else 0
        today_progress  = today_stats.today_progress  if today_stats else 0
        vocab_completed = today_stats.vocab_completed  if today_stats else 0
        rc_passages     = today_stats.rc_passages      if today_stats else 0
        va_questions    = today_stats.va_questions     if today_stats else 0

        hours      = study_minutes // 60
        minutes    = study_minutes % 60
        study_time = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

        return {
            "name":           user.name.split()[0],
            "day_count":      day_count,
            "streak":         streak,
            "study_time":     study_time if study_minutes > 0 else "0m",
            "today_progress": today_progress,
            "practice_stats": {
                "vocab": {"done": vocab_completed, "total": 20},
                "rc":    {"passages": rc_passages},
                "va":    {"types": "PJ • OOO • PS"},
            },
            "test_stats": {
                "rc": {"label": "Not attempted"},
                "va": {"label": "Not attempted"},
            },
            "week_activity": week_activity,
        }

    async def get_practice_modules(self, user_id: uuid.UUID, db: AsyncSession):
        from app.models.vocab import VocabWord, VocabProgress
        from app.models.rc import RCAttempt, RCPassage
        from app.models.article import Article, ArticleProgress
        from app.models.va import VAQuestion, VAProgress

        # ── Vocab Progress ──────────────────────────────────────────────────
        total_vocab_result = await db.execute(
            select(func.count()).select_from(VocabWord).where(VocabWord.is_active == True)
        )
        completed_vocab_result = await db.execute(
            select(func.count()).select_from(VocabProgress).where(
                and_(VocabProgress.user_id == user_id, VocabProgress.is_completed == True)
            )
        )
        total_vocab = total_vocab_result.scalar() or 1
        done_vocab  = completed_vocab_result.scalar() or 0
        vocab_pct   = round((done_vocab / total_vocab) * 100)

        # ── RC Progress ─────────────────────────────────────────────────────
        total_rc_result = await db.execute(
            select(func.count()).select_from(RCPassage).where(RCPassage.is_active == True)
        )
        attempted_rc_result = await db.execute(
            select(func.count(RCAttempt.passage_id.distinct())).where(
                RCAttempt.user_id == user_id
            )
        )
        total_rc = total_rc_result.scalar() or 1
        done_rc  = attempted_rc_result.scalar() or 0
        rc_pct   = round((done_rc / total_rc) * 100)

        # ── Essay / Article Progress ─────────────────────────────────────────
        total_articles_result = await db.execute(
            select(func.count()).select_from(Article).where(Article.is_active == True)
        )
        read_articles_result = await db.execute(
            select(func.count()).select_from(ArticleProgress).where(
                and_(ArticleProgress.user_id == user_id, ArticleProgress.is_read == True)
            )
        )
        total_articles = total_articles_result.scalar() or 1
        read_articles  = read_articles_result.scalar() or 0
        essay_pct      = round((read_articles / total_articles) * 100)

        # ── VA Progress ──────────────────────────────────────────────────────
        total_va_result = await db.execute(
            select(func.count()).select_from(VAQuestion).where(VAQuestion.is_active == True)
        )
        va_progress_result = await db.execute(
            select(VAProgress).where(VAProgress.user_id == user_id)
        )
        total_va    = total_va_result.scalar() or 1
        va_progress = va_progress_result.scalar_one_or_none()
        done_va     = va_progress.total_correct if va_progress else 0
        va_pct      = round((done_va / total_va) * 100)

        # ── Today's goal stats ───────────────────────────────────────────────
        today_result = await db.execute(
            select(UserDailyStats).where(
                and_(
                    UserDailyStats.user_id == user_id,
                    UserDailyStats.date    == date.today()
                )
            )
        )
        today          = today_result.scalar_one_or_none()
        goal_completed = today.vocab_completed if today else 0

        # ── Streak ───────────────────────────────────────────────────────────
        streak_result = await db.execute(
            select(UserStreak).where(UserStreak.user_id == user_id)
        )
        streak_obj = streak_result.scalar_one_or_none()
        streak     = streak_obj.current_streak if streak_obj else 0

        # ── Modules ───────────────────────────────────────────────────────────
        modules = [
            {
                "id":          "vocab",
                "title":       "VOCAB",
                "description": f"Master 500+ high-frequency CAT words. {done_vocab}/{total_vocab} completed.",
                "progress":    vocab_pct,
                "tag":         "HIGH PRIORITY" if vocab_pct < 50 else None,
            },
            {
                "id":          "rc",
                "title":       "RC",
                "description": f"Reading Comprehension passages. {done_rc}/{total_rc} attempted.",
                "progress":    rc_pct,
                "tag":         "NEW CONTENT" if done_rc == 0 else None,
            },
            {
                "id":          "essay",
                "title":       "ESSAY / ARTICLE",
                "description": f"Daily editorial analysis. {read_articles}/{total_articles} articles read.",
                "progress":    essay_pct,
                "tag":         None,
            },
            {
                "id":          "va",
                "title":       "VERBAL ABILITY",
                "description": f"Parajumbles, Odd One Out, Para Summary. {done_va}/{total_va} correct.",
                "progress":    va_pct,  # ✅ dynamic
                "tag":         "NEW CONTENT" if done_va == 0 else None,
            },
        ]

        return {
            "modules":        modules,
            "goal_completed": goal_completed,
            "goal_total":     20,
            "streak":         streak,
        }

home_service = HomeService()