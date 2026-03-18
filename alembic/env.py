import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.db.config import settings
from app.db.database import Base

# Alembic Config
config = context.config
fileConfig(config.config_file_name)

# DATABASE_URL .env se lega
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Saare models yahan import karne honge
# Jaise jaise models banayenge, yahan add karte jayenge
# from app.models.user import User

from app.account.models import User
from app.models.vocab import VocabWord, VocabProgress, VocabBookmark
from app.models.daily_stats import UserDailyStats, UserStreak
from app.models.rc import RCPassage, RCQuestion, RCOption, RCAttempt, RCAttemptAnswer  
from app.models.article import Article, ArticleAnalysis, ArticleBookmark, ArticleProgress
from app.models.va import VAQuestion, VAAttempt, VAProgress   
from app.models.notification import Notification  



target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = create_async_engine(settings.DATABASE_URL)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())