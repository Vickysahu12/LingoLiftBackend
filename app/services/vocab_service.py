from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException, status
from typing import List
import random
from app.models.vocab import VocabWord, VocabProgress, VocabBookmark
from app.account.models import User
from app.schemas.vocabs import VocabQuizSubmit, BookmarkToggleRequest, VocabWordCreate
import uuid
from app.services.streak_service import update_streak  # ← top pe add karo

class VocabService:

    # ─── All Words (with user progress) ──────────────────────
    async def get_words(self, user_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(
            select(VocabWord)
            .where(VocabWord.is_active == True)
            .order_by(VocabWord.order_index)
        )
        words = result.scalars().all()

        # User ka progress fetch karo
        progress_result = await db.execute(
            select(VocabProgress)
            .where(VocabProgress.user_id == user_id)
        )
        progress_map = {p.word_id: p for p in progress_result.scalars().all()}

        # User ke bookmarks fetch karo
        bookmark_result = await db.execute(
            select(VocabBookmark)
            .where(VocabBookmark.user_id == user_id)
        )
        bookmark_set = {b.word_id for b in bookmark_result.scalars().all()}

        # Response banao
        response = []
        for word in words:
            prog = progress_map.get(word.id)
            response.append({
                "id":           word.id,
                "word":         word.word,
                "phonetic":     word.phonetic,
                "definition":   word.definition,
                "synonyms":     word.synonyms or [],
                "antonyms":     word.antonyms or [],
                "context":      word.context,
                "source":       word.source,
                "article_url":  word.article_url,
                "tip":          word.tip,
                "tag":          word.tag,
                "is_completed": prog.is_completed if prog else False,
                "is_bookmarked": word.id in bookmark_set,
            })
        return response

    # ─── Quiz for a word ──────────────────────────────────────
    async def get_quiz(self, word_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(
            select(VocabWord).where(VocabWord.id == word_id)
        )
        word = result.scalar_one_or_none()
        if not word:
            raise HTTPException(status_code=404, detail="Word not found")

        # Options: 1 correct (first synonym) + 3 wrong (antonyms + random)
        correct_answer = word.synonyms[0] if word.synonyms else word.definition[:30]
        wrong_options  = (word.antonyms or [])[:3]

        # Agar antonyms kam hain toh dummy options
        while len(wrong_options) < 3:
            wrong_options.append(f"Option {len(wrong_options) + 2}")

        options = [correct_answer] + wrong_options
        random.shuffle(options)
        correct_index = options.index(correct_answer)

        return {
            "word_id":     word.id,
            "word":        word.word,
            "phonetic":    word.phonetic,
            "question":    "Select the most accurate meaning:",
            "options":     options,
            "explanation": word.tip or word.definition,
            "_correct_index": correct_index  # internally use karenge
        }

    # ─── Submit Quiz Answer ───────────────────────────────────
    async def submit_quiz(self, user_id: uuid.UUID, data: VocabQuizSubmit, db: AsyncSession):
        is_correct = data.selected == data.correct

        # Progress update ya create
        result = await db.execute(
            select(VocabProgress).where(
                and_(
                    VocabProgress.user_id == user_id,
                    VocabProgress.word_id == data.word_id
                )
            )
        )
        progress = result.scalar_one_or_none()

        if progress:
            progress.attempts    += 1
            progress.is_correct   = is_correct
            progress.is_completed = True
        else:
            progress = VocabProgress(
                user_id      = user_id,
                word_id      = data.word_id,
                is_correct   = is_correct,
                is_completed = True,
                attempts     = 1
            )
            db.add(progress)

        await db.flush()

        # Word fetch for explanation
        word_result = await db.execute(select(VocabWord).where(VocabWord.id == data.word_id))
        word = word_result.scalar_one_or_none()

        await update_streak(user_id=user_id, db=db)  # ← yahan

        return {
            "is_correct":    is_correct,
            "explanation":   word.tip if word else None,
            "correct_index": data.correct
        }

    # ─── Bookmark Toggle ──────────────────────────────────────
    async def toggle_bookmark(self, user_id: uuid.UUID, word_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(
            select(VocabBookmark).where(
                and_(
                    VocabBookmark.user_id == user_id,
                    VocabBookmark.word_id == word_id
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            await db.delete(existing)
            await db.flush()
            return {"is_bookmarked": False, "message": "Bookmark removed"}
        else:
            bookmark = VocabBookmark(user_id=user_id, word_id=word_id)
            db.add(bookmark)
            await db.flush()
            return {"is_bookmarked": True, "message": "Bookmarked!"}

    # ─── Admin: Add Word ──────────────────────────────────────
    async def add_word(self, data: VocabWordCreate, db: AsyncSession):
        result = await db.execute(select(VocabWord).where(VocabWord.word == data.word))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Word already exists")

        word = VocabWord(**data.model_dump())
        db.add(word)
        await db.flush()
        return word

    # ─── User Vocab Stats ─────────────────────────────────────
    async def get_stats(self, user_id: uuid.UUID, db: AsyncSession):
        total = await db.execute(select(func.count()).where(VocabWord.is_active == True))
        completed = await db.execute(
            select(func.count()).where(
                and_(VocabProgress.user_id == user_id, VocabProgress.is_completed == True)
            )
        )
        bookmarked = await db.execute(
            select(func.count()).where(VocabBookmark.user_id == user_id)
        )
        correct = await db.execute(
            select(func.count()).where(
                and_(
                    VocabProgress.user_id == user_id,
                    VocabProgress.is_correct == True
                )
            )
        )

        total_count     = total.scalar() or 0
        completed_count = completed.scalar() or 0
        bookmark_count  = bookmarked.scalar() or 0
        correct_count   = correct.scalar() or 0
        accuracy        = round((correct_count / completed_count * 100), 1) if completed_count > 0 else 0.0

        return {
            "total_words":      total_count,
            "completed_words":  completed_count,
            "bookmarked_words": bookmark_count,
            "accuracy":         accuracy
        }

vocab_service = VocabService()