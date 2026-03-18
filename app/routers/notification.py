from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.dependencies import get_current_user, get_admin_user
from app.account.models import User
from app.schemas.notification import NotificationCreate
from app.services.notification_service import notification_service
import uuid

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# ─── User Routes ──────────────────────────────────────────
@router.get("")
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await notification_service.get_notifications(current_user.id, db)

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await notification_service.get_unread_count(current_user.id, db)

@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await notification_service.mark_read(notification_id, current_user.id, db)

@router.post("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await notification_service.mark_all_read(current_user.id, db)

@router.delete("/{notification_id}")
async def dismiss(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await notification_service.dismiss(notification_id, current_user.id, db)

# ─── Admin Routes ─────────────────────────────────────────
@router.post("/admin/send", dependencies=[Depends(get_admin_user)])
async def send_notification(
    data: NotificationCreate,
    db: AsyncSession = Depends(get_db)
):
    return await notification_service.send_notification(data, db)