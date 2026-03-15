from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.database import Base

class VocabWord(Base):
    __tablename__ = "vocab_words"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    word          = Column(String(100), nullable=False, unique=True)
    phonetic      = Column(String(100), nullable=True)
    definition    = Column(Text, nullable=False)
    synonyms      = Column(JSON, default=[])      # ["word1", "word2"]
    antonyms      = Column(JSON, default=[])      # ["word1", "word2"]
    context       = Column(Text, nullable=True)   # editorial context
    source        = Column(String(100), nullable=True)  # "THE HINDU"
    article_url   = Column(Text, nullable=True)
    tip           = Column(Text, nullable=True)   # CAT exam tip
    tag           = Column(String(50), nullable=True)   # "HIGH FREQUENCY"
    order_index   = Column(Integer, default=0)    # display order
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    progress      = relationship("VocabProgress", back_populates="word", cascade="all, delete")
    bookmarks     = relationship("VocabBookmark", back_populates="word", cascade="all, delete")

    def __repr__(self):
        return f"<VocabWord {self.word}>"


class VocabProgress(Base):
    __tablename__ = "vocab_progress"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id       = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    word_id       = Column(UUID(as_uuid=True), ForeignKey("vocab_words.id", ondelete="CASCADE"), nullable=False)
    is_completed  = Column(Boolean, default=False)
    is_correct    = Column(Boolean, nullable=True)   # quiz mein correct tha?
    attempts      = Column(Integer, default=0)
    last_seen_at  = Column(DateTime(timezone=True), server_default=func.now())
    completed_at  = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user          = relationship("User", backref="vocab_progress")
    word          = relationship("VocabWord", back_populates="progress")


class VocabBookmark(Base):
    __tablename__ = "vocab_bookmarks"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id       = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    word_id       = Column(UUID(as_uuid=True), ForeignKey("vocab_words.id", ondelete="CASCADE"), nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user          = relationship("User", backref="vocab_bookmarks")
    word          = relationship("VocabWord", back_populates="bookmarks")