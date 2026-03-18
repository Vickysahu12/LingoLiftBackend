from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    # nullable = True kyunki broadcast notifications hoti hain (sab users ke liye)

    category     = Column(String(30), nullable=False)
    # 'mock' | 'study' | 'achievement' | 'update'

    icon         = Column(String(10), nullable=True)    # emoji
    title        = Column(String(255), nullable=False)
    desc         = Column(Text, nullable=False)
    action_screen = Column(String(100), nullable=True)  # navigate karne ke liye
    is_read      = Column(Boolean, default=False)
    is_broadcast = Column(Boolean, default=False)       # sabke liye hai?
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    user         = relationship("User", backref="notifications")

    def __repr__(self):
        return f"<Notification {self.title}>"