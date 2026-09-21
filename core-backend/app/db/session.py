from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
    echo=settings.debug,
)


# ============================================================
# SESSION FACTORY
# ============================================================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ============================================================
# STARTUP DATABASE CHECK
# ============================================================

async def check_database_connection() -> None:
    """
    Verify that PostgreSQL is reachable.

    This is executed during FastAPI startup.

    If the database cannot be reached, this function raises
    an exception and FastAPI startup fails.
    """

    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


# ============================================================
# DATABASE SHUTDOWN
# ============================================================

async def close_database() -> None:
    """
    Dispose the SQLAlchemy connection pool during shutdown.
    """

    await engine.dispose()


# ============================================================
# REQUEST-SCOPED DATABASE SESSION
# ============================================================

async def get_db() -> AsyncGenerator[
    AsyncSession,
    None,
]:
    """
    Create one AsyncSession for one request.

    The session is never shared between requests.

    Successful request:
        yield
        commit
        close

    Failed request:
        rollback
        close
    """

    async with AsyncSessionLocal() as session:

        try:
            yield session

            await session.commit()

        except Exception:
            await session.rollback()
            raise

        finally:
            await session.close()