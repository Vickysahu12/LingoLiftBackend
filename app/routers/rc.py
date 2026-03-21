from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.dependencies import get_current_user, get_admin_user
from app.account.models import User
from app.schemas.Rc import RCPassageCreate, RCAttemptSubmit,RCPassageResponse
from app.services.rc_service import rc_service
import uuid

router = APIRouter(prefix="/rc", tags=["Reading Comprehension"])

# ─── User Routes ──────────────────────────────────────────
@router.get("/sessions")
async def get_passages(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await rc_service.get_passages(db)

@router.get("/sessions/{passage_id}",response_model=RCPassageResponse)
async def get_passage(
    passage_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await rc_service.get_passage(passage_id, db)

@router.post("/sessions/{passage_id}/submit")
async def submit_attempt(
    data: RCAttemptSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await rc_service.submit_attempt(current_user.id, data, db)

# ─── Admin Routes ─────────────────────────────────────────
@router.post("/admin/passages", dependencies=[Depends(get_admin_user)])
async def add_passage(
    data: RCPassageCreate,
    db: AsyncSession = Depends(get_db)
):
    return await rc_service.add_passage(data, db)