from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.database import Base

class VAQuestion(Base):
    __tablename__ = "va_questions"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    question_type = Column(String(30), nullable=False)
    # 'para_jumble' | 'odd_one_out' | 'para_summary'
    
    question     = Column(Text, nullable=False)
    options      = Column(JSON, default=[])
    # [{"id": "A", "text": "...", "highlight": null}]
    
    correct      = Column(String(5), nullable=False)  # "A", "B", "C", "D"
    explanation  = Column(JSON, nullable=True)
    # {"correct": "A", "why": "explanation text"}
    
    strategy     = Column(JSON, nullable=True)
    # {"icon": "🔍", "label": "Opening Sentence Strategy"}
    
    difficulty   = Column(String(20), default="Medium")
    is_active    = Column(Boolean, default=True)
    order_index  = Column(Integer, default=0)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    attempts     = relationship("VAAttempt", back_populates="question", cascade="all, delete")

    def __repr__(self):
        return f"<VAQuestion {self.question_type} - {self.id}>"


class VAAttempt(Base):
    __tablename__ = "va_attempts"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id  = Column(UUID(as_uuid=True), ForeignKey("va_questions.id", ondelete="CASCADE"), nullable=False)
    question_type = Column(String(30), nullable=False)
    selected     = Column(String(5), nullable=True)   # "A", "B", etc
    is_correct   = Column(Boolean, default=False)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user         = relationship("User", backref="va_attempts")
    question     = relationship("VAQuestion", back_populates="attempts")


class VAProgress(Base):
    __tablename__ = "va_progress"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id        = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Per type progress
    pj_attempted   = Column(Integer, default=0)   # para jumble
    pj_correct     = Column(Integer, default=0)
    
    ooo_attempted  = Column(Integer, default=0)   # odd one out
    ooo_correct    = Column(Integer, default=0)
    
    ps_attempted   = Column(Integer, default=0)   # para summary
    ps_correct     = Column(Integer, default=0)
    
    total_attempted = Column(Integer, default=0)
    total_correct   = Column(Integer, default=0)
    
    updated_at     = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user           = relationship("User", backref="va_progress")