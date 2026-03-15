from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.dependencies import get_current_user, get_admin_user
from app.account.models import User
from app.schemas.vocabs import VocabQuizSubmit, BookmarkToggleRequest, VocabWordCreate
from app.services.vocab_service import vocab_service
import uuid

router = APIRouter(prefix="/vocab", tags=["Vocabulary"])

# ─── User Routes ──────────────────────────────────────────
@router.get("/words")
async def get_words(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await vocab_service.get_words(current_user.id, db)

@router.get("/words/{word_id}/quiz")
async def get_quiz(
    word_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await vocab_service.get_quiz(word_id, db)

@router.post("/quiz/submit")
async def submit_quiz(
    data: VocabQuizSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await vocab_service.submit_quiz(current_user.id, data, db)

@router.post("/bookmark")
async def toggle_bookmark(
    data: BookmarkToggleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await vocab_service.toggle_bookmark(current_user.id, data.word_id, db)

@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await vocab_service.get_stats(current_user.id, db)

# ─── Admin Routes ─────────────────────────────────────────
@router.post("/admin/words", dependencies=[Depends(get_admin_user)])
async def add_word(
    data: VocabWordCreate,
    db: AsyncSession = Depends(get_db)
):
    return await vocab_service.add_word(data, db)