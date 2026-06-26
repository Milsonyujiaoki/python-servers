from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.settings import Settings

settings = Settings()

# Convert DATABASE_URL to async version if needed
database_url = settings.DB_URL
if database_url.startswith("sqlite://"):
    # For SQLite, use aiosqlite
    database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
elif database_url.startswith("postgresql://"):
    # For PostgreSQL, use asyncpg
    database_url = database_url.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )

engine = create_async_engine(database_url, echo=False)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
