from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import HTTPException
import uuid
from datetime import date
from app.models.rc import RCPassage, RCQuestion, RCOption, RCAttempt, RCAttemptAnswer
from app.models.daily_stats import UserDailyStats
from app.schemas.Rc import RCPassageCreate, RCAttemptSubmit
from app.services.streak_service import update_streak

class RCService:

    async def get_passages(self, user_id: uuid.UUID, db: AsyncSession):
        today = date.today()

        # ── Aaj ke attempted passage IDs ──────────────────────────────────
        today_result = await db.execute(
            select(RCAttempt.passage_id).where(
                and_(
                    RCAttempt.user_id == user_id,
                    func.date(RCAttempt.completed_at) == today
                )
            )
        )
        attempted_today_ids = set(r[0] for r in today_result.all())

        # ── Kabhi bhi attempted passage IDs (all time) ────────────────────
        all_time_result = await db.execute(
            select(RCAttempt.passage_id.distinct()).where(
                RCAttempt.user_id == user_id
            )
        )
        all_attempted_ids = set(r[0] for r in all_time_result.all())

        # ── Saare active passages ─────────────────────────────────────────
        passages_result = await db.execute(
            select(RCPassage)
            .where(RCPassage.is_active == True)
            .order_by(RCPassage.order_index)
        )
        all_passages = passages_result.scalars().all()

        # ── Pehle unke jo kabhi attempt nahi hue ─────────────────────────
        unattempted = [p for p in all_passages if p.id not in all_attempted_ids]

        # Agar saare complete ho gaye — cycle restart
        pool = unattempted if unattempted else all_passages

        # Har din sirf 2 passages
        daily = pool[:2]

        # ── Response ──────────────────────────────────────────────────────
        response = []
        for p in daily:
            q_result = await db.execute(
                select(RCQuestion).where(RCQuestion.passage_id == p.id)
            )
            questions = q_result.scalars().all()

            response.append({
                "id":              p.id,
                "title":           p.title,
                "subject":         p.subject,
                "difficulty":      p.difficulty,
                "source":          p.source,
                "total_questions": len(questions),
                "is_completed":    p.id in attempted_today_ids,  # ✅ aaj done ya nahi
            })

        return response

    async def get_attempted_today(self, user_id: uuid.UUID, db: AsyncSession):
        today = date.today()
        result = await db.execute(
            select(RCAttempt).where(
                and_(
                    RCAttempt.user_id == user_id,
                    func.date(RCAttempt.completed_at) == today
                )
            )
        )
        attempts = result.scalars().all()
        return [{"passage_id": str(a.passage_id)} for a in attempts]

    async def get_passage(self, passage_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(
            select(RCPassage).where(RCPassage.id == passage_id)
        )
        passage = result.scalar_one_or_none()

        if not passage:
            raise HTTPException(status_code=404, detail="Passage not found")

        q_result = await db.execute(
            select(RCQuestion)
            .where(RCQuestion.passage_id == passage_id)
            .order_by(RCQuestion.order_index)
        )
        questions = q_result.scalars().all()

        questions_data = []

        for q in questions:
            opt_result = await db.execute(
                select(RCOption)
                .where(RCOption.question_id == q.id)
                .order_by(RCOption.order_index)
            )
            options = opt_result.scalars().all()

            correct_index = 0
            options_data  = []

            for idx, o in enumerate(options):
                if o.is_correct:
                    correct_index = idx
                options_data.append({
                    "id":          o.id,
                    "option_text": o.option_text,
                    "order_index": o.order_index,
                })

            questions_data.append({
                "id":            q.id,
                "question":      q.question,
                "difficulty":    q.difficulty,
                "analysis":      q.analysis,
                "order_index":   q.order_index,
                "correct_index": correct_index,
                "options":       options_data
            })

        return {
            "id":         passage.id,
            "title":      passage.title,
            "body":       passage.body,
            "subject":    passage.subject,
            "difficulty": passage.difficulty,
            "source":     passage.source,
            "questions":  questions_data
        }

    async def submit_attempt(self, user_id: uuid.UUID, data: RCAttemptSubmit, db: AsyncSession):
        correct = sum(1 for a in data.answers if a.selected_index == a.correct_index)
        skipped = sum(1 for a in data.answers if a.selected_index is None)
        wrong   = len(data.answers) - correct - skipped
        total   = len(data.answers)
        score   = round((correct / total) * 100, 1) if total > 0 else 0.0

        attempt = RCAttempt(
            user_id    = user_id,
            passage_id = data.passage_id,
            score      = score,
            correct    = correct,
            wrong      = wrong,
            skipped    = skipped,
            time_taken = data.time_taken
        )
        db.add(attempt)
        await db.flush()

        for ans in data.answers:
            answer = RCAttemptAnswer(
                attempt_id     = attempt.id,
                question_id    = ans.question_id,
                selected_index = ans.selected_index,
                correct_index  = ans.correct_index,
                is_correct     = ans.selected_index == ans.correct_index
            )
            db.add(answer)

        await db.flush()

        


        # Daily stats update
        today = date.today()
        stats_result = await db.execute(
            select(UserDailyStats).where(
                and_(
                    UserDailyStats.user_id == user_id,
                    UserDailyStats.date    == today
                )
            )
        )
        stats = stats_result.scalar_one_or_none()
        if stats:
            stats.rc_passages += 1
        else:
            stats = UserDailyStats(
                user_id     = user_id,
                date        = today,
                rc_passages = 1
            )
            db.add(stats)
        await db.flush()
        await update_streak(user_id=user_id, db=db) 


        return {
            "attempt_id": attempt.id,
            "score":      score,
            "correct":    correct,
            "wrong":      wrong,
            "skipped":    skipped,
            "time_taken": data.time_taken,
            "total":      total
        }

    async def add_passage(self, data: RCPassageCreate, db: AsyncSession):
        passage = RCPassage(
            title       = data.title,
            body        = data.body,
            subject     = data.subject,
            difficulty  = data.difficulty,
            source      = data.source,
            order_index = data.order_index
        )
        db.add(passage)
        await db.flush()

        for i, q_data in enumerate(data.questions):
            question = RCQuestion(
                passage_id  = passage.id,
                question    = q_data.question,
                difficulty  = q_data.difficulty,
                analysis    = q_data.analysis,
                order_index = i
            )
            db.add(question)
            await db.flush()

            for j, opt in enumerate(q_data.options):
                option = RCOption(
                    question_id = question.id,
                    option_text = opt.option_text,
                    is_correct  = opt.is_correct,
                    order_index = j
                )
                db.add(option)

        await db.flush()
        return {"message": "Passage added successfully", "id": str(passage.id)}

rc_service = RCService()