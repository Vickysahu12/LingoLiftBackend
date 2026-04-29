from fastapi import FastAPI,Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine,Base,get_db
from app.routers import auth,Vocabss,Home,rc,article,va,notification
from app.routers.mock import router as mock_router, attempts_router
from app.routers.profile import router as profile_router
from app.routers import admin



app = FastAPI(
    title="LingoLift Backend",
    description="CAT VARC section backend",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(Vocabss.router)
app.include_router(Home.router)
app.include_router(rc.router)
app.include_router(article.router)
app.include_router(va.router)
app.include_router(notification.router)
app.include_router(mock_router)
app.include_router(attempts_router)
app.include_router(profile_router)
app.include_router(admin.router)

# Startup pe DB connection check and health check
@app.get("/make-admin")
async def make_admin(email: str, db: AsyncSession = Depends(get_db)):
    await db.execute(
        text("UPDATE users SET is_admin = true WHERE email = :email"),
        {"email": email}
    )
    await db.commit()
    return {"message": "Done!"}

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        print("✅ Database connected successfully!")

@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "ok", "message": "LingoLift API is running!"}