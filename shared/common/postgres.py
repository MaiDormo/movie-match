import os
from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def _get_database_url() -> str:
    user: Optional[str] = os.getenv("POSTGRES_USER")
    password: Optional[str] = os.getenv("POSTGRES_PASSWORD")
    host: Optional[str] = os.getenv("POSTGRES_HOST")
    db: Optional[str] = os.getenv("POSTGRES_DB")
    if not all([user, password, host, db]):
        raise RuntimeError("Missing PostgreSQL environment variables")
    return f"postgresql+asyncpg://{user}:{password}@{host}:5432/{db}"


engine = create_async_engine(_get_database_url(), echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
