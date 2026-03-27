from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import HTTPException
import uuid
from app.models.va import VAQuestion, VAAttempt, VAProgress
from app.models.daily_stats import UserStreak
from app.account.models import User
from app.schemas.va import VAQuestionCreate, VASubmitRequest
from app.services.streak_service import update_streak

class VAService:

    # ─── Hub Stats ────────────────────────────────────────────
    async def get_hub(self, user: User, db: AsyncSession):
        streak_result = await db.execute(
            select(UserStreak).where(UserStreak.user_id == user.id)
        )
        streak_obj = streak_result.scalar_one_or_none()
        streak = streak_obj.current_streak if streak_obj else 0

        prog_result = await db.execute(
            select(VAProgress).where(VAProgress.user_id == user.id)
        )
        progress = prog_result.scalar_one_or_none()

        async def get_total(qtype):
            r = await db.execute(
                select(func.count()).select_from(VAQuestion).where(
                    and_(VAQuestion.question_type == qtype, VAQuestion.is_active == True)
                )
            )
            return r.scalar() or 1

        pj_total  = await get_total("para_jumble")
        ooo_total = await get_total("odd_one_out")
        ps_total  = await get_total("para_summary")

        pj_pct  = round((progress.pj_correct  / pj_total)  * 100) if progress else 0
        ooo_pct = round((progress.ooo_correct / ooo_total) * 100) if progress else 0
        ps_pct  = round((progress.ps_correct  / ps_total)  * 100) if progress else 0

        total_progress = round((pj_pct + ooo_pct + ps_pct) / 3)

        def get_tag(pct):
            if pct == 0:   return {"label": "NEW",         "bg": "#EFF6FF", "color": "#2563EB"}
            if pct < 50:   return {"label": "STARTED",     "bg": "#FEF3C7", "color": "#D97706"}
            if pct < 100:  return {"label": "IN PROGRESS", "bg": "#DCFCE7", "color": "#16A34A"}
            return              {"label": "COMPLETED",    "bg": "#DCFCE7", "color": "#16A34A"}

        return {
            "user_name":      user.name.split()[0],
            "streak":         streak,
            "total_progress": total_progress,
            "modules": [
                {
                    "id":       "para_jumble",
                    "title":    "Parajumbles",
                    "subtitle": "Mastering chronological flow",
                    "progress": pj_pct,
                    "icon":     "🔀",
                    "tag":      get_tag(pj_pct),
                    "route":    "Parajumble"
                },
                {
                    "id":       "odd_one_out",
                    "title":    "Odd One Out",
                    "subtitle": "Identifying the outlier theme",
                    "progress": ooo_pct,
                    "icon":     "🎯",
                    "tag":      get_tag(ooo_pct),
                    "route":    "OddOne"
                },
                {
                    "id":       "para_summary",
                    "title":    "Para Summary",
                    "subtitle": "Extracting the core essence",
                    "progress": ps_pct,
                    "icon":     "📝",
                    "tag":      get_tag(ps_pct),
                    "route":    "Parasum"
                },
            ]
        }

    # ─── Get Questions by Type ────────────────────────────────
    async def get_questions(self, question_type: str, db: AsyncSession):
        valid_types = ["para_jumble", "odd_one_out", "para_summary"]
        if question_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid type. Use: {valid_types}")

        result = await db.execute(
            select(VAQuestion).where(
                and_(
                    VAQuestion.question_type == question_type,
                    VAQuestion.is_active == True
                )
            ).order_by(VAQuestion.order_index)
        )
        questions = result.scalars().all()

        return [
            {
                "id":            q.id,
                "question_type": q.question_type,
                "question":      q.question,
                "options":       q.options,
                "sentences":     q.sentences,   # ✅ YE ADD KIYA — para_jumble ke liye
                "strategy":      q.strategy,
                "difficulty":    q.difficulty,
            }
            for q in questions
        ]

    # ─── Submit Answer ────────────────────────────────────────
    async def submit_answer(self, user_id: uuid.UUID, data: VASubmitRequest, db: AsyncSession):
        result = await db.execute(
            select(VAQuestion).where(VAQuestion.id == data.question_id)
        )
        question = result.scalar_one_or_none()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        is_correct = data.selected == question.correct

        attempt = VAAttempt(
            user_id       = user_id,
            question_id   = data.question_id,
            question_type = data.question_type,
            selected      = data.selected,
            is_correct    = is_correct
        )
        db.add(attempt)

        prog_result = await db.execute(
            select(VAProgress).where(VAProgress.user_id == user_id)
        )
        progress = prog_result.scalar_one_or_none()

        if not progress:
         progress = VAProgress(
        user_id=user_id,
        pj_attempted=0, pj_correct=0,
        ooo_attempted=0, ooo_correct=0,
        ps_attempted=0, ps_correct=0,
        total_attempted=0, total_correct=0
       )
        db.add(progress) 

        if data.question_type == "para_jumble":
            progress.pj_attempted  += 1
            if is_correct: progress.pj_correct += 1
        elif data.question_type == "odd_one_out":
            progress.ooo_attempted += 1
            if is_correct: progress.ooo_correct += 1
        elif data.question_type == "para_summary":
            progress.ps_attempted  += 1
            if is_correct: progress.ps_correct += 1

        progress.total_attempted += 1
        if is_correct: progress.total_correct += 1

        await db.flush()

        await update_streak(user_id=user_id, db=db)  # ← yahan

        return {
            "is_correct":  is_correct,
            "correct":     question.correct,
            "explanation": question.explanation
        }

    # ─── User Progress ────────────────────────────────────────
    async def get_progress(self, user_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(
            select(VAProgress).where(VAProgress.user_id == user_id)
        )
        progress = result.scalar_one_or_none()

        if not progress:
            return {
                "pj_attempted": 0, "pj_correct": 0,
                "ooo_attempted": 0, "ooo_correct": 0,
                "ps_attempted": 0, "ps_correct": 0,
                "total_attempted": 0, "total_correct": 0,
                "accuracy": 0.0
            }

        accuracy = round(
            (progress.total_correct / progress.total_attempted * 100), 1
        ) if progress.total_attempted > 0 else 0.0

        return {
            "pj_attempted":    progress.pj_attempted,
            "pj_correct":      progress.pj_correct,
            "ooo_attempted":   progress.ooo_attempted,
            "ooo_correct":     progress.ooo_correct,
            "ps_attempted":    progress.ps_attempted,
            "ps_correct":      progress.ps_correct,
            "total_attempted": progress.total_attempted,
            "total_correct":   progress.total_correct,
            "accuracy":        accuracy
        }

    # ─── Admin: Add Question ──────────────────────────────────
    async def add_question(self, data: VAQuestionCreate, db: AsyncSession):
        question = VAQuestion(
            question_type = data.question_type,
            question      = data.question,
            options       = [o.model_dump() for o in data.options],
            correct       = data.correct,
            explanation   = data.explanation,
            strategy      = data.strategy,
            sentences     = data.sentences,   # ✅ sentences bhi save hoga
            difficulty    = data.difficulty,
            order_index   = data.order_index
        )
        db.add(question)
        await db.flush()
        return {"message": "Question added", "id": str(question.id)}

va_service = VAService()