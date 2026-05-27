from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.db.database import get_db
from app.dependencies import get_current_user, get_admin_user
from app.account.models import User
from app.schemas.va import VAQuestionCreate, VAQuestionUpdate, VAReorderRequest, VASubmitRequest
from app.services.va_service import va_service

router = APIRouter(prefix="/va", tags=["Verbal Ability"])


# ─── User Routes ──────────────────────────────────────────────────────────────

@router.get("/hub")
async def get_hub(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await va_service.get_hub(current_user, db)


@router.get("/questions")
async def get_questions(
    type: str = Query(..., description="para_jumble | odd_one_out | para_summary"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await va_service.get_questions(type, db)


@router.post("/submit")
async def submit_answer(
    data: VASubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await va_service.submit_answer(current_user.id, data, db)


@router.get("/progress")
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await va_service.get_progress(current_user.id, db)


# ─── Admin Routes ─────────────────────────────────────────────────────────────

@router.get("/admin/questions", dependencies=[Depends(get_admin_user)])
async def list_questions_admin(
    question_type: Optional[str] = Query(None, description="para_jumble | odd_one_out | para_summary"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await va_service.list_questions_admin(db, question_type, page, page_size)


@router.post("/admin/questions", dependencies=[Depends(get_admin_user)])
async def add_question(
    data: VAQuestionCreate,
    db: AsyncSession = Depends(get_db),
):
    return await va_service.add_question(data, db)


@router.put("/admin/questions/{question_id}", dependencies=[Depends(get_admin_user)])
async def update_question(
    question_id: uuid.UUID,
    data: VAQuestionUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await va_service.update_question(question_id, data, db)


@router.delete("/admin/questions/{question_id}", dependencies=[Depends(get_admin_user)])
async def delete_question(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await va_service.delete_question(question_id, db)


@router.patch("/admin/questions/reorder", dependencies=[Depends(get_admin_user)])
async def reorder_questions(
    data: VAReorderRequest,
    db: AsyncSession = Depends(get_db),
):
    return await va_service.reorder_questions(data, db)