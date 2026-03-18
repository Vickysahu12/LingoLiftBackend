from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from fastapi import HTTPException
from datetime import datetime, timezone
import uuid
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

class NotificationService:

    # ─── Time ago format ──────────────────────────────────────
    def _time_ago(self, created_at: datetime) -> str:
        now = datetime.now(timezone.utc)
        diff = now - created_at.replace(tzinfo=timezone.utc)
        seconds = diff.total_seconds()

        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            mins = int(seconds // 60)
            return f"{mins} min ago"
        elif seconds < 86400:
            hrs = int(seconds // 3600)
            return f"{hrs} hr ago"
        elif seconds < 172800:
            return "Yesterday"
        else:
            days = int(seconds // 86400)
            return f"{days} days ago"

    # ─── Get All Notifications ────────────────────────────────
    async def get_notifications(self, user_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(
            select(Notification).where(
                or_(
                    Notification.user_id == user_id,       # user specific
                    Notification.is_broadcast == True       # ya broadcast
                )
            ).order_by(Notification.created_at.desc())
        )
        notifications = result.scalars().all()

        unread_count = sum(1 for n in notifications if not n.is_read)

        return {
            "notifications": [
                {
                    "id":            n.id,
                    "category":      n.category,
                    "icon":          n.icon,
                    "title":         n.title,
                    "desc":          n.desc,
                    "action_screen": n.action_screen,
                    "is_read":       n.is_read,
                    "time":          self._time_ago(n.created_at),
                    "unread":        not n.is_read,
                }
                for n in notifications
            ],
            "unread_count": unread_count
        }

    # ─── Mark One Read ────────────────────────────────────────
    async def mark_read(self, notification_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    or_(
                        Notification.user_id == user_id,
                        Notification.is_broadcast == True
                    )
                )
            )
        )
        notification = result.scalar_one_or_none()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        notification.is_read = True
        await db.flush()
        return {"success": True}

    # ─── Mark All Read ────────────────────────────────────────
    async def mark_all_read(self, user_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(
            select(Notification).where(
                or_(
                    Notification.user_id == user_id,
                    Notification.is_broadcast == True
                )
            )
        )
        notifications = result.scalars().all()

        for n in notifications:
            n.is_read = True

        await db.flush()
        return {"success": True, "marked": len(notifications)}

    # ─── Dismiss (Delete) ─────────────────────────────────────
    async def dismiss(self, notification_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    or_(
                        Notification.user_id == user_id,
                        Notification.is_broadcast == True
                    )
                )
            )
        )
        notification = result.scalar_one_or_none()
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        await db.delete(notification)
        await db.flush()
        return {"success": True}

    # ─── Unread Count ─────────────────────────────────────────
    async def get_unread_count(self, user_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(
            select(Notification).where(
                and_(
                    or_(
                        Notification.user_id == user_id,
                        Notification.is_broadcast == True
                    ),
                    Notification.is_read == False
                )
            )
        )
        count = len(result.scalars().all())
        return {"unread_count": count}

    # ─── Admin: Send Notification ─────────────────────────────
    async def send_notification(self, data: NotificationCreate, db: AsyncSession):
        notification = Notification(
            user_id       = data.user_id,         # None = broadcast
            category      = data.category,
            icon          = data.icon,
            title         = data.title,
            desc          = data.desc,
            action_screen = data.action_screen,
            is_broadcast  = data.user_id is None   # user_id nahi = broadcast
        )
        db.add(notification)
        await db.flush()

        target = "all users" if data.user_id is None else str(data.user_id)
        return {"message": f"Notification sent to {target}", "id": str(notification.id)}

notification_service = NotificationService()