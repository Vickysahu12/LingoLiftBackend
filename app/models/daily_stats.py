from sqlalchemy import Column, Boolean, DateTime, Integer, Float, Date, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.database import Base

class UserDailyStats(Base):
    __tablename__ = "user_daily_stats"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id             = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date                = Column(Date, nullable=False)  # today's date

    # Time tracking
    study_minutes       = Column(Integer, default=0)

    # Practice counts
    vocab_completed     = Column(Integer, default=0)
    rc_passages         = Column(Integer, default=0)
    va_questions        = Column(Integer, default=0)

    # Progress percentage (0-100)
    today_progress      = Column(Float, default=0.0)

    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user                = relationship("User", backref="daily_stats")

    __table_args__ = (
        # Ek user ka ek din mein sirf ek record
        __import__('sqlalchemy').UniqueConstraint('user_id', 'date', name='uq_user_date'),
    )


class UserStreak(Base):
    __tablename__ = "user_streaks"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id         = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    current_streak  = Column(Integer, default=0)
    longest_streak  = Column(Integer, default=0)
    last_active_date= Column(Date, nullable=True)
    week_activity   = Column(JSON, default=[False]*7)  # [Mon, Tue, Wed, Thu, Fri, Sat, Sun]
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user            = relationship("User", backref="streak")