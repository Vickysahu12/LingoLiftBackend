from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class NotificationResponse(BaseModel):
    id:            uuid.UUID
    category:      str
    icon:          Optional[str] = None
    title:         str
    desc:          str
    action_screen: Optional[str] = None
    is_read:       bool
    time:          str  # "10 min ago" format
    model_config   = {"from_attributes": True}

class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    unread_count:  int

# Admin ke liye
class NotificationCreate(BaseModel):
    category:      str
    icon:          Optional[str] = None
    title:         str
    desc:          str
    action_screen: Optional[str] = None
    user_id:       Optional[uuid.UUID] = None  # None = broadcast