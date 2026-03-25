# ─── EXISTING User model mein sirf ye 3 fields add karo ─────────────────────
# Baki sab already exist karta hai (phone, profile_pic, name, email)
# Stats (streak, tests_given, avg_score, rank) → computed from TestAttempt — NO new columns

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Google OAuth fields
    google_id = Column(String(255), unique=True, nullable=True, index=True)

    # Email/Password fields
    email    = Column(String(255), unique=True, nullable=False, index=True)
    name     = Column(String(255), nullable=False)
    phone    = Column(String(15),  unique=True, nullable=True)
    hashed_password = Column(Text, nullable=True)
    profile_pic     = Column(Text, nullable=True)

    # ── ADD THESE 3 FIELDS ────────────────────────────────────────────────────
    target_exam = Column(String(50),  nullable=True)   # "CAT 2025"
    target_year = Column(String(10),  nullable=True)   # "2025"
    current_streak = Column(Integer,  default=0)       # updated nightly / on activity
    # ─────────────────────────────────────────────────────────────────────────

    # App fields
    is_active  = Column(Boolean, default=True)
    is_admin   = Column(Boolean, default=False)
    auth_provider = Column(String(20), default="email")

    # Email Verification
    is_verified    = Column(Boolean, default=False)
    otp_code       = Column(String(6), nullable=True)
    otp_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User {self.email}>"