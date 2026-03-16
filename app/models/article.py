from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.database import Base

class Article(Base):
    __tablename__ = "articles"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title       = Column(String(255), nullable=False)
    tag         = Column(String(50), nullable=True)      # Economics, Philosophy, etc.
    meta        = Column(String(100), nullable=True)     # "8 min read • Medium"
    level       = Column(String(20), default="Medium")   # Easy/Medium/Hard
    content     = Column(JSON, default=[])               # list of paragraphs
    image_url   = Column(Text, nullable=True)
    is_active   = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    analysis    = relationship("ArticleAnalysis", back_populates="article", uselist=False, cascade="all, delete")
    bookmarks   = relationship("ArticleBookmark", back_populates="article", cascade="all, delete")
    progress    = relationship("ArticleProgress", back_populates="article", cascade="all, delete")

    def __repr__(self):
        return f"<Article {self.title}>"


class ArticleAnalysis(Base):
    __tablename__ = "article_analysis"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id   = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, unique=True)
    score        = Column(Integer, default=0)
    difficulty   = Column(String(20), default="Medium")
    central_idea = Column(Text, nullable=True)
    tone         = Column(JSON, nullable=True)       # {main, options, explanation}
    structure    = Column(JSON, default=[])          # [{heading, text}]
    arguments    = Column(JSON, default=[])          # [{claim, evidence}]
    cat_tip      = Column(Text, nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    article      = relationship("Article", back_populates="analysis")


class ArticleBookmark(Base):
    __tablename__ = "article_bookmarks"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user       = relationship("User", backref="article_bookmarks")
    article    = relationship("Article", back_populates="bookmarks")


class ArticleProgress(Base):
    __tablename__ = "article_progress"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id        = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id     = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    is_read        = Column(Boolean, default=False)
    is_analyzed    = Column(Boolean, default=False)
    time_spent     = Column(Integer, default=0)      # seconds
    updated_at     = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user           = relationship("User", backref="article_progress")
    article        = relationship("Article", back_populates="progress")