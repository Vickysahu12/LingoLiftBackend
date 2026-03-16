from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.dependencies import get_current_user, get_admin_user
from app.account.models import User
from app.schemas.va import VAQuestionCreate, VASubmitRequest
from app.services.va_service import va_service
from typing import Optional

router = APIRouter(prefix="/va", tags=["Verbal Ability"])

# ─── User Routes ──────────────────────────────────────────
@router.get("/hub")
async def get_hub(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await va_service.get_hub(current_user, db)

@router.get("/questions")
async def get_questions(
    type: str = Query(..., description="para_jumble | odd_one_out | para_summary"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await va_service.get_questions(type, db)

@router.post("/submit")
async def submit_answer(
    data: VASubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await va_service.submit_answer(current_user.id, data, db)

@router.get("/progress")
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await va_service.get_progress(current_user.id, db)

# ─── Admin Routes ─────────────────────────────────────────
@router.post("/admin/questions", dependencies=[Depends(get_admin_user)])
async def add_question(
    data: VAQuestionCreate,
    db: AsyncSession = Depends(get_db)
):
    return await va_service.add_question(data, db)