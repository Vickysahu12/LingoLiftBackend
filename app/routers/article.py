from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.dependencies import get_current_user, get_admin_user
from app.account.models import User
from app.schemas.Article import ArticleCreate, ArticleAnalysisCreate, ArticleTimeTrack
from app.services.article_service import article_service
import uuid
from typing import Optional

router = APIRouter(prefix="/articles", tags=["Articles"])

# ─── User Routes ──────────────────────────────────────────
@router.get("")
async def get_articles(
    tag: Optional[str] = Query(None),
    q:   Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await article_service.get_articles(current_user.id, db, tag, q)

@router.get("/{article_id}")
async def get_article(
    article_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await article_service.get_article(article_id, current_user.id, db)

@router.post("/{article_id}/bookmark")
async def toggle_bookmark(
    article_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await article_service.toggle_bookmark(current_user.id, article_id, db)

@router.post("/{article_id}/read")
async def mark_read(
    article_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await article_service.mark_read(current_user.id, article_id, db)

@router.post("/{article_id}/time")
async def track_time(
    article_id: uuid.UUID,
    data: ArticleTimeTrack,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await article_service.track_time(current_user.id, article_id, data.seconds_spent, db)

# ─── Admin Routes ─────────────────────────────────────────
@router.post("/admin/articles", dependencies=[Depends(get_admin_user)])
async def add_article(
    data: ArticleCreate,
    db: AsyncSession = Depends(get_db)
):
    return await article_service.add_article(data, db)

@router.post("/admin/articles/{article_id}/analysis", dependencies=[Depends(get_admin_user)])
async def add_analysis(
    article_id: uuid.UUID,
    data: ArticleAnalysisCreate,
    db: AsyncSession = Depends(get_db)
):
    return await article_service.add_analysis(article_id, data, db)