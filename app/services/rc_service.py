from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException
from typing import List
import uuid
from app.models.rc import RCPassage, RCQuestion, RCOption, RCAttempt, RCAttemptAnswer
from app.schemas.Rc import RCPassageCreate, RCAttemptSubmit

class RCService:

    # ─── All Passages List ────────────────────────────────────
    async def get_passages(self, db: AsyncSession):
        result = await db.execute(
            select(RCPassage)
            .where(RCPassage.is_active == True)
            .order_by(RCPassage.order_index)
        )
        passages = result.scalars().all()

        response = []
        for p in passages:
            # Questions count
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
                "total_questions": len(questions)
            })
        return response

    # ─── Single Passage + Questions ───────────────────────────
    async def get_passage(self, passage_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(
            select(RCPassage).where(RCPassage.id == passage_id)
        )
        passage = result.scalar_one_or_none()
        if not passage:
            raise HTTPException(status_code=404, detail="Passage not found")

        # Questions with options
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
            questions_data.append({
                "id":          q.id,
                "question":    q.question,
                "difficulty":  q.difficulty,
                "analysis":    q.analysis,
                "order_index": q.order_index,
                "options": [
                    {
                        "id":          o.id,
                        "option_text": o.option_text,
                        "order_index": o.order_index,
                    }
                    for o in options
                ]
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

    # ─── Submit Attempt ───────────────────────────────────────
    async def submit_attempt(self, user_id: uuid.UUID, data: RCAttemptSubmit, db: AsyncSession):
        correct = sum(1 for a in data.answers if a.selected_index == a.correct_index)
        skipped = sum(1 for a in data.answers if a.selected_index is None)
        wrong   = len(data.answers) - correct - skipped
        total   = len(data.answers)
        score   = round((correct / total) * 100, 1) if total > 0 else 0.0

        # Save attempt
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

        # Save answers
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

        return {
            "attempt_id": attempt.id,
            "score":      score,
            "correct":    correct,
            "wrong":      wrong,
            "skipped":    skipped,
            "time_taken": data.time_taken,
            "total":      total
        }

    # ─── Admin: Add Passage ───────────────────────────────────
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

        # Add questions + options
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