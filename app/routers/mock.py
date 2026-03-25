from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.db.database import get_db
from app.dependencies import get_current_user
from app.account.models import User
from app.schemas.mock import (
    MockListItem, MockDetailResponse, ExamConfigResponse,
    SubmitAttemptRequest, SubmitAttemptResponse,
    SaveProgressRequest, SolutionsResponse,
    AttemptHistoryItem,
)
from app.services.mock_services import mock_service

router = APIRouter(prefix="/mocks", tags=["MockPortal"])


# ─── MOCK LIST ────────────────────────────────────────────────────────────────
# MockListScreen.jsx → GET /mocks/
# Returns all active mocks with user's last attempt score

@router.get("", response_model=list[MockListItem])
async def get_mocks(
    type:  Optional[str] = Query(None, description="Filter: full | half | topic"),
    current_user: User        = Depends(get_current_user),
    db: AsyncSession          = Depends(get_db),
):
    return await mock_service.get_mocks(current_user.id, db, type_filter=type)


# ─── MOCK DETAIL ──────────────────────────────────────────────────────────────
# MockDetailScreen.jsx → GET /mocks/{mock_id}
# Returns full detail: sections, marking, rules, syllabus, instructions, attempt info

@router.get("/{mock_id}", response_model=MockDetailResponse)
async def get_mock_detail(
    mock_id: uuid.UUID,
    current_user: User   = Depends(get_current_user),
    db: AsyncSession     = Depends(get_db),
):
    return await mock_service.get_mock_detail(mock_id, current_user.id, db)


# ─── EXAM CONFIG ──────────────────────────────────────────────────────────────
# TestInterfaceScreen.jsx → GET /mocks/{mock_id}/exam-config
# Returns passages + questions (WITHOUT answers) + creates a new attempt
# Frontend stores returned attempt_id for save/submit calls

@router.get("/{mock_id}/exam-config", response_model=ExamConfigResponse)
async def get_exam_config(
    mock_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession   = Depends(get_db),
):
    return await mock_service.get_exam_config(mock_id, current_user.id, db)


# ─── USER ATTEMPT HISTORY ─────────────────────────────────────────────────────
# MockDetailScreen "Previous Attempt" strip → GET /mocks/{mock_id}/attempts

@router.get("/{mock_id}/attempts", response_model=list[AttemptHistoryItem])
async def get_user_attempts(
    mock_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession   = Depends(get_db),
):
    return await mock_service.get_user_attempts(mock_id, current_user.id, db)


# ─── SAVE PROGRESS (AUTO-SAVE) ────────────────────────────────────────────────
# TestInterfaceScreen.jsx → POST /attempts/{attempt_id}/save
# Call every 30s to persist questionMeta without submitting

attempts_router = APIRouter(prefix="/attempts", tags=["MockPortal"])

@attempts_router.post("/{attempt_id}/save")
async def save_progress(
    attempt_id: uuid.UUID,
    data: SaveProgressRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession   = Depends(get_db),
):
    return await mock_service.save_progress(attempt_id, current_user.id, data, db)


# ─── SUBMIT TEST ──────────────────────────────────────────────────────────────
# TestInterfaceScreen SubmitModal → POST /attempts/{attempt_id}/submit
# Sends full questionMeta + timeTaken, returns computed result
# ResultScreen then navigates to /attempts/{attempt_id}/solutions

@attempts_router.post("/{attempt_id}/submit", response_model=SubmitAttemptResponse)
async def submit_attempt(
    attempt_id: uuid.UUID,
    data: SubmitAttemptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession   = Depends(get_db),
):
    return await mock_service.submit_attempt(attempt_id, current_user.id, data, db)


# ─── SOLUTIONS ────────────────────────────────────────────────────────────────
# SolutionScreen.jsx → GET /attempts/{attempt_id}/solutions
# Only available after submit — reveals correct_option/correct_answer

@attempts_router.get("/{attempt_id}/solutions", response_model=SolutionsResponse)
async def get_solutions(
    attempt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession   = Depends(get_db),
):
    return await mock_service.get_solutions(attempt_id, current_user.id, db)