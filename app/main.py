from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine,Base
from app.routers import auth,Vocabss,Home,rc,article,va,notification
from app.routers.mock import router as mock_router, attempts_router


app = FastAPI(
    title="LingoLift Backend",
    description="CAT VARC section backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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

# Startup pe DB connection check
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        print("✅ Database connected successfully!")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "LingoLift API is running!"}