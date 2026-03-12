from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone
from app.db.database import Base

class User(Base):
    __tablename__ = "users"