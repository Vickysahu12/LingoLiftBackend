from sqlalchemy import Column, String, Boolean, DateTime, Text
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
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(15), unique=True, nullable=True)
    hashed_password = Column(Text, nullable=True)  # Google users ka null hoga
    profile_pic = Column(Text, nullable=True)

    # App fields
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    auth_provider = Column(String(20), default="email")  # 'email' | 'google'

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User {self.email}>"