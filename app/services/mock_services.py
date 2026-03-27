from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import HTTPException
import uuid
from datetime import datetime, timezone
from app.services.streak_service import update_streak

from app.models.mock import (
    MockTest, MockSection, MarkingScheme, MockRule,
    MockSyllabus, MockInstruction, Passage, MockQuestion,
    TestAttempt, QuestionResponse,
    MockType, AttemptStatus, QuestionStatus, QuestionType,
)
from app.schemas.mock import (
    SubmitAttemptRequest, SaveProgressRequest,
    QuestionMetaIn,
)


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _format_attempts(count: int) -> str:
    """Format attempt count like frontend: 1234 → '1.2k'"""
    if count >= 1000:
        return f"{count / 1000:.1f}k"
    return str(count) if count > 0 else None


def _marking_to_display(scheme: MarkingScheme) -> dict:
    """Convert DB marking scheme to frontend display strings"""
    return {
        "correct":     f"+{scheme.correct_marks} Marks",
        "correct_sub": scheme.correct_sub,
        "wrong":       f"{scheme.incorrect_marks} Mark",
        "wrong_sub":   scheme.wrong_sub,
        "tita":        f"{scheme.tita_marks} Marks" if scheme.has_tita else "N/A",
        "tita_sub":    scheme.tita_sub,
        "has_tita":    scheme.has_tita,
    }


def _compute_section_result(responses: list, questions: list) -> dict:
    """Compute correct/wrong/unattempted for a set of questions"""
    q_map  = {str(q.id): q for q in questions}
    r_map  = {str(r.question_id): r for r in responses}

    correct = wrong = unattempted = 0

    for q in questions:
        r = r_map.get(str(q.id))

        no_answer = (
            not r
            or r.status in (QuestionStatus.not_visited, QuestionStatus.visited_not_answered)
            or (r.status == QuestionStatus.marked_review and r.selected is None and not (r.tita_answer or "").strip())
        )

        if no_answer:
            unattempted += 1
            continue

        if q.type == QuestionType.tita:
            ans      = (r.tita_answer or "").strip().upper()
            expected = (q.correct_answer or "").strip().upper()
            if ans == expected:
                correct += 1
            else:
                unattempted += 1   # TITA wrong → no negative, counts as unattempted
        else:
            if r.selected == q.correct_option:
                correct += 1
            elif r.selected is not None:
                wrong += 1
            else:
                unattempted += 1

    score     = correct * 3 + wrong * (-1)
    max_score = len(questions) * 3
    attempted = correct + wrong
    accuracy  = round((correct / attempted * 100), 1) if attempted > 0 else 0.0

    return {
        "total": len(questions), "correct": correct, "wrong": wrong,
        "unattempted": unattempted, "attempted": attempted,
        "score": score, "max_score": max_score, "accuracy": accuracy,
    }


# ─── MOCK SERVICE ─────────────────────────────────────────────────────────────

class MockService:

    # ── GET /mocks/  (list) ───────────────────────────────────────────────────
    async def get_mocks(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
        type_filter: str = None,
    ):
        query = (
            select(MockTest)
            .where(MockTest.is_active == True)
            .order_by(MockTest.order_index)
        )
        result  = await db.execute(query)
        mocks   = result.scalars().all()

        # Fetch user's last attempt scores in one query
        attempts_result = await db.execute(
            select(TestAttempt)
            .where(
                and_(
                    TestAttempt.user_id == user_id,
                    TestAttempt.status  == AttemptStatus.submitted,
                )
            )
            .order_by(TestAttempt.attempt_number.desc())
        )
        all_attempts = attempts_result.scalars().all()

        # Build map: mock_id → latest attempt
        latest_attempt_map: dict[str, TestAttempt] = {}
        for attempt in all_attempts:
            key = str(attempt.mock_id)
            if key not in latest_attempt_map:
                latest_attempt_map[key] = attempt

        response = []
        for mock in mocks:
            if type_filter and type_filter != "all" and mock.type != type_filter:
                continue

            latest  = latest_attempt_map.get(str(mock.id))
            response.append({
                "id":               mock.id,
                "title":            mock.title,
                "subtitle":         mock.subtitle,
                "type":             mock.type,
                "icon":             mock.icon,
                "badge":            mock.badge,
                "difficulty":       mock.difficulty,
                "total_questions":  mock.total_questions,
                "duration":         mock.total_duration,
                "max_score":        mock.max_score,
                "attempts":         _format_attempts(mock.attempt_count),
                "topics":           mock.topics or [],
                "is_attempted":     latest is not None,
                "last_score":       latest.score if latest else None,
            })
        return response

    # ── GET /mocks/{mock_id}  (detail) ───────────────────────────────────────
    async def get_mock_detail(
        self,
        mock_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
    ):
        # Fetch mock
        result = await db.execute(select(MockTest).where(MockTest.id == mock_id))
        mock   = result.scalar_one_or_none()
        if not mock:
            raise HTTPException(status_code=404, detail="Mock test not found")

        # Fetch related data
        sections_res = await db.execute(
            select(MockSection).where(MockSection.mock_id == mock_id).order_by(MockSection.order_index)
        )
        marking_res = await db.execute(
            select(MarkingScheme).where(MarkingScheme.mock_id == mock_id)
        )
        rules_res = await db.execute(
            select(MockRule).where(MockRule.mock_id == mock_id).order_by(MockRule.order_index)
        )
        syllabus_res = await db.execute(
            select(MockSyllabus).where(MockSyllabus.mock_id == mock_id).order_by(MockSyllabus.order_index)
        )
        instructions_res = await db.execute(
            select(MockInstruction).where(MockInstruction.mock_id == mock_id).order_by(MockInstruction.order_index)
        )

        sections     = sections_res.scalars().all()
        marking      = marking_res.scalar_one_or_none()
        rules        = rules_res.scalars().all()
        syllabus     = syllabus_res.scalars().all()
        instructions = instructions_res.scalars().all()

        # User attempt info
        attempts_res = await db.execute(
            select(TestAttempt)
            .where(
                and_(
                    TestAttempt.user_id == user_id,
                    TestAttempt.mock_id == mock_id,
                    TestAttempt.status  == AttemptStatus.submitted,
                )
            )
            .order_by(TestAttempt.attempt_number.desc())
        )
        user_attempts  = attempts_res.scalars().all()
        latest_attempt = user_attempts[0] if user_attempts else None
        attempt_number = (len(user_attempts) + 1)  # next attempt number

        return {
            "id":              mock.id,
            "title":           mock.title,
            "subtitle":        mock.subtitle,
            "description":     mock.description,
            "type":            mock.type,
            "icon":            mock.icon,
            "badge":           mock.badge,
            "difficulty":      mock.difficulty,
            "total_duration":  mock.total_duration,
            "duration_secs":   mock.duration_secs,
            "total_questions": mock.total_questions,
            "max_score":       mock.max_score,
            "sections":        [
                {
                    "id":           s.id,
                    "section_key":  s.section_key,
                    "label":        s.label,
                    "icon":         s.icon,
                    "duration":     s.duration,
                    "questions":    s.questions,
                    "breakdown":    s.breakdown,
                    "color":        s.color,
                    "is_locked":    s.is_locked,
                }
                for s in sections
            ],
            "marking":         _marking_to_display(marking) if marking else None,
            "rules":           [{"icon": r.icon, "label": r.label} for r in rules],
            "syllabus":        [{"label": s.label, "covered": s.covered} for s in syllabus],
            "instructions":    [i.text for i in instructions],
            "attempt_number":  attempt_number,
            "is_attempted":    latest_attempt is not None,
            "last_score":      latest_attempt.score if latest_attempt else None,
            "last_attempt_id": latest_attempt.id if latest_attempt else None,
        }

    # ── GET /mocks/{mock_id}/exam-config  (TestInterface) ────────────────────
    async def get_exam_config(
        self,
        mock_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
    ):
        result = await db.execute(select(MockTest).where(MockTest.id == mock_id))
        mock   = result.scalar_one_or_none()
        if not mock:
            raise HTTPException(status_code=404, detail="Mock test not found")

        if mock.badge and mock.badge.value == "locked":
            raise HTTPException(status_code=403, detail="This test is locked. Upgrade to unlock.")

        # Create a new attempt
        # Count existing attempts for attempt_number
        count_res = await db.execute(
            select(func.count(TestAttempt.id)).where(
                and_(TestAttempt.user_id == user_id, TestAttempt.mock_id == mock_id)
            )
        )
        existing_count = count_res.scalar() or 0
        attempt = TestAttempt(
            user_id        = user_id,
            mock_id        = mock_id,
            status         = AttemptStatus.in_progress,
            attempt_number = existing_count + 1,
            max_score      = mock.max_score,
        )
        db.add(attempt)
        await db.flush()

        # Increment platform attempt count
        mock.attempt_count += 1
        await db.flush()

        # Fetch sections (unlocked only active)
        sections_res = await db.execute(
            select(MockSection)
            .where(MockSection.mock_id == mock_id)
            .order_by(MockSection.order_index)
        )
        sections = sections_res.scalars().all()

        sections_out = []
        for section in sections:
            # Fetch passages for section
            passages_res = await db.execute(
                select(Passage).where(Passage.section_id == section.id)
            )
            passages = passages_res.scalars().all()

            # Fetch questions — NOTE: correct_option / correct_answer NOT exposed here
            questions_res = await db.execute(
                select(MockQuestion)
                .where(MockQuestion.section_id == section.id)
                .order_by(MockQuestion.number)
            )
            questions = questions_res.scalars().all()

            # Build passage_key → passage mapping for questions
            passage_key_map = {str(p.id): p.passage_key for p in passages}

            sections_out.append({
                "id":              section.id,
                "section_key":     section.section_key,
                "label":           section.label,
                "icon":            section.icon,
                "total_questions": section.questions,
                "duration_secs":   section.duration_secs,
                "is_locked":       section.is_locked,
                "passages": [
                    {
                        "id":          p.id,
                        "passage_key": p.passage_key,
                        "label":       p.label,
                        "title":       p.title,
                        "content":     p.content or [],
                    }
                    for p in passages
                ],
                "questions": [
                    {
                        "id":         q.id,
                        "number":     q.number,
                        "type":       q.type,
                        "text":       q.text,
                        "options":    q.options,
                        "hint":       q.hint,
                        "passage_id": passage_key_map.get(str(q.passage_id)) if q.passage_id else None,
                        "marks": {
                            "correct":   q.marks_correct,
                            "incorrect": q.marks_incorrect,
                        },
                    }
                    for q in questions
                ],
            })

        return {
            "mock_id":       mock.id,
            "test_title":    mock.title,
            "subject":       "VARC",
            "total_seconds": mock.duration_secs,
            "sections":      sections_out,
            "attempt_id":    attempt.id,
        }

    # ── POST /attempts/{attempt_id}/save  (auto-save) ────────────────────────
    async def save_progress(
        self,
        attempt_id: uuid.UUID,
        user_id: uuid.UUID,
        data: SaveProgressRequest,
        db: AsyncSession,
    ):
        attempt = await self._get_attempt(attempt_id, user_id, db)
        if attempt.status != AttemptStatus.in_progress:
            raise HTTPException(status_code=400, detail="Attempt already submitted")

        await self._upsert_responses(attempt_id, data.question_meta, db)
        attempt.time_taken_secs = data.time_taken_secs
        await db.flush()
        return {"saved": True}

    # ── POST /attempts/{attempt_id}/submit ────────────────────────────────────
    async def submit_attempt(
        self,
        attempt_id: uuid.UUID,
        user_id: uuid.UUID,
        data: SubmitAttemptRequest,
        db: AsyncSession,
    ):
        attempt = await self._get_attempt(attempt_id, user_id, db)
        if attempt.status == AttemptStatus.submitted:
            raise HTTPException(status_code=400, detail="Attempt already submitted")

        # Upsert all question responses
        await self._upsert_responses(attempt_id, data.question_meta, db)

        # Fetch all questions for this mock (active sections only)
        sections_res = await db.execute(
            select(MockSection).where(
                and_(MockSection.mock_id == attempt.mock_id, MockSection.is_locked == False)
            )
        )
        active_sections = sections_res.scalars().all()
        section_ids     = [s.id for s in active_sections]

        questions_res = await db.execute(
            select(MockQuestion).where(MockQuestion.section_id.in_(section_ids))
        )
        questions = questions_res.scalars().all()

        # Fetch all responses for this attempt
        responses_res = await db.execute(
            select(QuestionResponse).where(QuestionResponse.attempt_id == attempt_id)
        )
        responses = responses_res.scalars().all()

        # Compute overall result
        overall = _compute_section_result(responses, questions)

        # Compute RC/VA breakdown
        rc_questions = [q for q in questions if q.passage_id is not None]
        va_questions = [q for q in questions if q.passage_id is None]
        rc_result    = _compute_section_result(responses, rc_questions) if rc_questions else None
        va_result    = _compute_section_result(responses, va_questions) if va_questions else None

        # Mark individual responses as correct/wrong
        r_map = {str(r.question_id): r for r in responses}
        q_map = {str(q.id): q for q in questions}
        for qid, resp in r_map.items():
            q = q_map.get(qid)
            if not q:
                continue
            if q.type == QuestionType.tita:
                ans = (resp.tita_answer or "").strip().upper()
                exp = (q.correct_answer or "").strip().upper()
                resp.is_correct = (ans == exp) if ans else None
            elif resp.selected is not None:
                resp.is_correct = (resp.selected == q.correct_option)
            else:
                resp.is_correct = None

        # Update attempt
        attempt.status          = AttemptStatus.submitted
        attempt.submitted_at    = datetime.now(timezone.utc)
        attempt.time_taken_secs = data.time_taken_secs
        attempt.score           = overall["score"]
        attempt.correct         = overall["correct"]
        attempt.wrong           = overall["wrong"]
        attempt.unattempted     = overall["unattempted"]
        attempt.accuracy        = overall["accuracy"]
        attempt.section_breakdown = {
            "rc": rc_result,
            "va": va_result,
        }
        await db.flush()
        await update_streak(user_id=user_id, db=db)  # ← yahan


        return {
            "attempt_id":      attempt.id,
            "mock_id":         attempt.mock_id,
            "status":          attempt.status,
            "score":           attempt.score,
            "max_score":       attempt.max_score,
            "correct":         attempt.correct,
            "wrong":           attempt.wrong,
            "unattempted":     attempt.unattempted,
            "attempted":       overall["attempted"],
            "accuracy":        attempt.accuracy,
            "time_taken_secs": attempt.time_taken_secs,
            "rc_result":       rc_result,
            "va_result":       va_result,
        }

    # ── GET /attempts/{attempt_id}/solutions ─────────────────────────────────
    async def get_solutions(
        self,
        attempt_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
    ):
        attempt = await self._get_attempt(attempt_id, user_id, db)
        if attempt.status != AttemptStatus.submitted:
            raise HTTPException(status_code=400, detail="Submit the test first to view solutions")

        # Fetch mock info
        mock_res = await db.execute(select(MockTest).where(MockTest.id == attempt.mock_id))
        mock     = mock_res.scalar_one_or_none()

        # Fetch sections
        sections_res = await db.execute(
            select(MockSection)
            .where(and_(MockSection.mock_id == attempt.mock_id, MockSection.is_locked == False))
            .order_by(MockSection.order_index)
        )
        sections = sections_res.scalars().all()

        # Fetch user responses
        responses_res = await db.execute(
            select(QuestionResponse).where(QuestionResponse.attempt_id == attempt_id)
        )
        responses = responses_res.scalars().all()
        r_map = {str(r.question_id): r for r in responses}

        sections_out = []
        for section in sections:
            passages_res = await db.execute(
                select(Passage).where(Passage.section_id == section.id)
            )
            passages = passages_res.scalars().all()
            passage_key_map = {str(p.id): p.passage_key for p in passages}

            questions_res = await db.execute(
                select(MockQuestion)
                .where(MockQuestion.section_id == section.id)
                .order_by(MockQuestion.number)
            )
            questions = questions_res.scalars().all()

            questions_out = []
            for q in questions:
                r = r_map.get(str(q.id))
                questions_out.append({
                    "id":             q.id,
                    "number":         q.number,
                    "type":           q.type,
                    "text":           q.text,
                    "options":        q.options,
                    "correct_option": q.correct_option,   # revealed here
                    "correct_answer": q.correct_answer,   # revealed here
                    "hint":           q.hint,
                    "explanation":    q.explanation,
                    "key_point":      q.key_point,
                    "passage_id":     passage_key_map.get(str(q.passage_id)) if q.passage_id else None,
                    "marks":          {"correct": q.marks_correct, "incorrect": q.marks_incorrect},
                    # user response
                    "user_status":   r.status  if r else QuestionStatus.not_visited,
                    "user_selected": r.selected if r else None,
                    "user_tita":     r.tita_answer if r else None,
                    "is_correct":    r.is_correct if r else None,
                })

            sections_out.append({
                "section_key": section.section_key,
                "label":       section.label,
                "passages": [
                    {
                        "id":          p.id,
                        "passage_key": p.passage_key,
                        "label":       p.label,
                        "title":       p.title,
                        "content":     p.content or [],
                    }
                    for p in passages
                ],
                "questions": questions_out,
            })

        return {
            "attempt_id":  attempt.id,
            "mock_id":     attempt.mock_id,
            "test_title":  mock.title if mock else "",
            "sections":    sections_out,
        }

    # ── GET /mocks/{mock_id}/attempts  (user history) ────────────────────────
    async def get_user_attempts(
        self,
        mock_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
    ):
        result = await db.execute(
            select(TestAttempt)
            .where(
                and_(
                    TestAttempt.user_id == user_id,
                    TestAttempt.mock_id == mock_id,
                )
            )
            .order_by(TestAttempt.attempt_number)
        )
        attempts = result.scalars().all()
        return [
            {
                "attempt_id":      a.id,
                "attempt_number":  a.attempt_number,
                "status":          a.status,
                "score":           a.score,
                "max_score":       a.max_score,
                "accuracy":        a.accuracy,
                "time_taken_secs": a.time_taken_secs,
                "submitted_at":    a.submitted_at,
            }
            for a in attempts
        ]

    # ─── Private helpers ──────────────────────────────────────────────────────

    async def _get_attempt(
        self,
        attempt_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> TestAttempt:
        result = await db.execute(
            select(TestAttempt).where(
                and_(
                    TestAttempt.id      == attempt_id,
                    TestAttempt.user_id == user_id,
                )
            )
        )
        attempt = result.scalar_one_or_none()
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        return attempt

    async def _upsert_responses(
        self,
        attempt_id: uuid.UUID,
        question_meta: dict[str, QuestionMetaIn],
        db: AsyncSession,
    ):
        """Upsert QuestionResponse rows from frontend questionMeta dict"""
        # Fetch existing responses
        existing_res = await db.execute(
            select(QuestionResponse).where(QuestionResponse.attempt_id == attempt_id)
        )
        existing = {str(r.question_id): r for r in existing_res.scalars().all()}

        for q_id_str, meta in question_meta.items():
            try:
                q_uuid = uuid.UUID(q_id_str)
            except ValueError:
                continue

            if q_id_str in existing:
                r = existing[q_id_str]
                r.status      = meta.status
                r.selected    = meta.selected
                r.tita_answer = meta.tita_answer
                r.time_spent_secs = meta.time_spent or 0
            else:
                r = QuestionResponse(
                    attempt_id  = attempt_id,
                    question_id = q_uuid,
                    status      = meta.status,
                    selected    = meta.selected,
                    tita_answer = meta.tita_answer,
                    time_spent_secs = meta.time_spent or 0,
                )
                db.add(r)

        await db.flush()


mock_service = MockService()