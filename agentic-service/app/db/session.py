from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


# ============================================================
# Engine
# ============================================================

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
    future=True,
)


# ============================================================
# Session Factory
# ============================================================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# ============================================================
# Startup Health Check
# ============================================================

async def check_database_connection() -> None:
    """
    Verify PostgreSQL connectivity.

    Called during application startup.
    """

    async with engine.connect() as connection:
        await connection.execute(
            text("SELECT 1")
        )


# ============================================================
# Request Dependency
# ============================================================

async def get_db() -> AsyncGenerator[
    AsyncSession,
    None,
]:
    """
    FastAPI database dependency.

    Provides one database session per request.
    """

    async with AsyncSessionLocal() as session:

        try:
            yield session

            await session.commit()

        except Exception:
            await session.rollback()
            raise


# ============================================================
# Service Context Manager
# ============================================================

@asynccontextmanager
async def get_db_session():
    """
    Provide a database session for repositories/services.

    Unlike get_db(), this is intended for normal Python
    service/repository code outside FastAPI dependency injection.

    Successful operation:
        commit

    Failed operation:
        rollback
    """

    async with AsyncSessionLocal() as session:

        try:

            yield session

            await session.commit()

        except Exception:

            await session.rollback()

            raise


# ============================================================
# Shutdown
# ============================================================

async def close_database() -> None:
    """
    Dispose the SQLAlchemy engine.
    """

    await engine.dispose()

    logger.info(
        "PostgreSQL connection pool disposed."
    )