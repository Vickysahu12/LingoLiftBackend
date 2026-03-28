from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    RESEND_API_KEY: str
    GMAIL_USER: str = ""
    GMAIL_PASSWORD: str = ""

    def model_post_init(self, __context):
        # Railway "postgres://" deta hai, asyncpg ko "postgresql+asyncpg://" chahiye
        if self.DATABASE_URL.startswith("postgres://"):
            object.__setattr__(
                self,
                "DATABASE_URL",
                self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
            )

    class Config:
        env_file = ".env"

settings = Settings()