from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException
import uuid
from app.models.article import Article, ArticleAnalysis, ArticleBookmark, ArticleProgress
from app.schemas.Article import ArticleCreate, ArticleAnalysisCreate

class ArticleService:

    # ─── Helper: user progress ────────────────────────────────
    async def _get_user_state(self, user_id: uuid.UUID, article_id: uuid.UUID, db: AsyncSession):
        bookmark = await db.execute(
            select(ArticleBookmark).where(
                and_(ArticleBookmark.user_id == user_id, ArticleBookmark.article_id == article_id)
            )
        )
        progress = await db.execute(
            select(ArticleProgress).where(
                and_(ArticleProgress.user_id == user_id, ArticleProgress.article_id == article_id)
            )
        )
        return (
            bookmark.scalar_one_or_none() is not None,
            progress.scalar_one_or_none()
        )

    # ─── Articles List ────────────────────────────────────────
    async def get_articles(self, user_id: uuid.UUID, db: AsyncSession, tag: str = None, q: str = None):
        query = select(Article).where(Article.is_active == True).order_by(Article.order_index)
        result = await db.execute(query)
        articles = result.scalars().all()

        response = []
        for article in articles:
            # Filter by tag
            if tag and tag != "All" and article.tag != tag:
                continue
            # Search filter
            if q and q.lower() not in article.title.lower() and q.lower() not in (article.tag or "").lower():
                continue

            is_bookmarked, progress = await self._get_user_state(user_id, article.id, db)

            response.append({
                "id":            article.id,
                "title":         article.title,
                "tag":           article.tag,
                "meta":          article.meta,
                "level":         article.level,
                "image_url":     article.image_url,
                "is_bookmarked": is_bookmarked,
                "is_read":       progress.is_read if progress else False,
            })
        return response

    # ─── Single Article ───────────────────────────────────────
    async def get_article(self, article_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(select(Article).where(Article.id == article_id))
        article = result.scalar_one_or_none()
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        is_bookmarked, progress = await self._get_user_state(user_id, article_id, db)

        # Analysis
        analysis_result = await db.execute(
            select(ArticleAnalysis).where(ArticleAnalysis.article_id == article_id)
        )
        analysis = analysis_result.scalar_one_or_none()

        return {
            "id":            article.id,
            "title":         article.title,
            "tag":           article.tag,
            "meta":          article.meta,
            "level":         article.level,
            "content":       article.content or [],
            "image_url":     article.image_url,
            "is_bookmarked": is_bookmarked,
            "is_read":       progress.is_read if progress else False,
            "analysis": {
                "score":        analysis.score,
                "difficulty":   analysis.difficulty,
                "central_idea": analysis.central_idea,
                "tone":         analysis.tone,
                "structure":    analysis.structure,
                "arguments":    analysis.arguments,
                "cat_tip":      analysis.cat_tip,
            } if analysis else None
        }

    # ─── Toggle Bookmark ──────────────────────────────────────
    async def toggle_bookmark(self, user_id: uuid.UUID, article_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(
            select(ArticleBookmark).where(
                and_(ArticleBookmark.user_id == user_id, ArticleBookmark.article_id == article_id)
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            await db.delete(existing)
            await db.flush()
            return {"is_bookmarked": False}
        else:
            bookmark = ArticleBookmark(user_id=user_id, article_id=article_id)
            db.add(bookmark)
            await db.flush()
            return {"is_bookmarked": True}

    # ─── Mark as Read ─────────────────────────────────────────
    async def mark_read(self, user_id: uuid.UUID, article_id: uuid.UUID, db: AsyncSession):
        result = await db.execute(
            select(ArticleProgress).where(
                and_(ArticleProgress.user_id == user_id, ArticleProgress.article_id == article_id)
            )
        )
        progress = result.scalar_one_or_none()

        if progress:
            progress.is_read = True
        else:
            progress = ArticleProgress(user_id=user_id, article_id=article_id, is_read=True)
            db.add(progress)

        await db.flush()
        return {"success": True}

    # ─── Track Read Time ──────────────────────────────────────
    async def track_time(self, user_id: uuid.UUID, article_id: uuid.UUID, seconds: int, db: AsyncSession):
        result = await db.execute(
            select(ArticleProgress).where(
                and_(ArticleProgress.user_id == user_id, ArticleProgress.article_id == article_id)
            )
        )
        progress = result.scalar_one_or_none()

        if progress:
            progress.time_spent += seconds
        else:
            progress = ArticleProgress(user_id=user_id, article_id=article_id, time_spent=seconds)
            db.add(progress)

        await db.flush()
        return {"success": True}

    # ─── Admin: Add Article ───────────────────────────────────
    async def add_article(self, data: ArticleCreate, db: AsyncSession):
        article = Article(**data.model_dump())
        db.add(article)
        await db.flush()
        return {"message": "Article added", "id": str(article.id)}

    # ─── Admin: Add Analysis ──────────────────────────────────
    async def add_analysis(self, article_id: uuid.UUID, data: ArticleAnalysisCreate, db: AsyncSession):
        # Article exists?
        result = await db.execute(select(Article).where(Article.id == article_id))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Article not found")

        # Already has analysis?
        existing = await db.execute(
            select(ArticleAnalysis).where(ArticleAnalysis.article_id == article_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Analysis already exists")

        analysis = ArticleAnalysis(article_id=article_id, **data.model_dump())
        db.add(analysis)
        await db.flush()
        return {"message": "Analysis added"}

article_service = ArticleService()