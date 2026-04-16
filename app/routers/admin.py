from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.dependencies import get_admin_user
from app.account.models import User
from app.models.rc import RCAttempt, RCPassage
from app.models.vocab import VocabWord
from datetime import datetime,extract


router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats", dependencies=[Depends(get_admin_user)])
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    total_users    = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    total_passages = (await db.execute(select(func.count()).where(RCPassage.is_active == True))).scalar() or 0
    total_attempts = (await db.execute(select(func.count()).select_from(RCAttempt))).scalar() or 0
    total_words    = (await db.execute(select(func.count()).where(VocabWord.is_active == True))).scalar() or 0

    return {
        "total_users":    total_users,
        "total_passages": total_passages,
        "total_attempts": total_attempts,
        "total_words":    total_words,
    }

@router.get("/stats/monthly", dependencies=[Depends(get_admin_user)])
async def get_monthly_stats(db: AsyncSession = Depends(get_db)):
    current_year = datetime.now().year
    
    result = await db.execute(
        select(
            extract('month', RCAttempt.completed_at).label('month'),
            func.count(RCAttempt.id).label('attempts')
        )
        .where(extract('year', RCAttempt.completed_at) == current_year)
        .group_by(extract('month', RCAttempt.completed_at))
        .order_by(extract('month', RCAttempt.completed_at))
    )
    rows = result.all()

    MONTHS = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
    data = {m: 0 for m in MONTHS}
    for row in rows:
        data[MONTHS[int(row.month) - 1]] = row.attempts

    return [{"month": m, "attempts": v} for m, v in data.items()]