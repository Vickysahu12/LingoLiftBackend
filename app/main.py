from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine,Base
from app.routers import auth,Vocabss,Home

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

# Startup pe DB connection check
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        print("✅ Database connected successfully!")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "LingoLift API is running!"}