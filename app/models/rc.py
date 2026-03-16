from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.database import Base

class RCPassage(Base):
    __tablename__ = "rc_passages"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title       = Column(String(255), nullable=False)
    body        = Column(Text, nullable=False)
    subject     = Column(String(100), default="Reading Comprehension")
    difficulty  = Column(String(20), default="Medium")  # Easy/Medium/Hard
    source      = Column(String(100), nullable=True)
    is_active   = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    questions   = relationship("RCQuestion", back_populates="passage", cascade="all, delete")
    attempts    = relationship("RCAttempt", back_populates="passage", cascade="all, delete")

    def __repr__(self):
        return f"<RCPassage {self.title}>"


class RCQuestion(Base):
    __tablename__ = "rc_questions"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    passage_id   = Column(UUID(as_uuid=True), ForeignKey("rc_passages.id", ondelete="CASCADE"), nullable=False)
    question     = Column(Text, nullable=False)
    difficulty   = Column(String(20), default="Medium")
    analysis     = Column(Text, nullable=True)   # explanation
    order_index  = Column(Integer, default=0)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    passage      = relationship("RCPassage", back_populates="questions")
    options      = relationship("RCOption", back_populates="question", cascade="all, delete")

    def __repr__(self):
        return f"<RCQuestion {self.id}>"


class RCOption(Base):
    __tablename__ = "rc_options"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("rc_questions.id", ondelete="CASCADE"), nullable=False)
    option_text = Column(Text, nullable=False)
    is_correct  = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)  # 0=A, 1=B, 2=C, 3=D

    # Relationship
    question    = relationship("RCQuestion", back_populates="options")


class RCAttempt(Base):
    __tablename__ = "rc_attempts"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    passage_id   = Column(UUID(as_uuid=True), ForeignKey("rc_passages.id", ondelete="CASCADE"), nullable=False)
    score        = Column(Float, default=0.0)       # percentage
    correct      = Column(Integer, default=0)
    wrong        = Column(Integer, default=0)
    skipped      = Column(Integer, default=0)
    time_taken   = Column(Integer, default=0)        # seconds
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user         = relationship("User", backref="rc_attempts")
    passage      = relationship("RCPassage", back_populates="attempts")
    answers      = relationship("RCAttemptAnswer", back_populates="attempt", cascade="all, delete")


class RCAttemptAnswer(Base):
    __tablename__ = "rc_attempt_answers"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id      = Column(UUID(as_uuid=True), ForeignKey("rc_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id     = Column(UUID(as_uuid=True), ForeignKey("rc_questions.id", ondelete="CASCADE"), nullable=False)
    selected_index  = Column(Integer, nullable=True)   # null = skipped
    correct_index   = Column(Integer, nullable=False)
    is_correct      = Column(Boolean, default=False)

    # Relationship
    attempt         = relationship("RCAttempt", back_populates="answers")