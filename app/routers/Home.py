from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.dependencies import get_current_user
from app.account.models import User
from app.services.home_service import home_service

router = APIRouter(prefix="/user", tags=["Home"])

@router.get("/home-stats")
async def get_home_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await home_service.get_home_stats(current_user, db)

@router.get("/practice-modules")
async def get_practice_modules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await home_service.get_practice_modules(current_user.id, db)