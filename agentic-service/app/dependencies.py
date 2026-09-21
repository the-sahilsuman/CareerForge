from __future__ import annotations

from uuid import UUID

from fastapi import (
    Depends,
    Header,
    HTTPException,
    status,
)
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.service import (
    AgentService,
    agent_service,
)
from app.core.config import settings
from app.core.redis import get_redis
from app.db.session import get_db


# ============================================================
# Database
# ============================================================


async def get_database_session(
    session: AsyncSession = Depends(get_db),
) -> AsyncSession:
    """
    FastAPI dependency for PostgreSQL sessions.
    """

    return session


# ============================================================
# Redis
# ============================================================


async def get_redis_client(
    redis: Redis = Depends(get_redis),
) -> Redis:
    """
    FastAPI dependency for Redis / ElastiCache.
    """

    return redis


# ============================================================
# Agent Service
# ============================================================


def get_agent_service() -> AgentService:
    """
    FastAPI dependency for the CareerForge agent.
    """

    return agent_service


# ============================================================
# Internal Core -> Agentic Authentication
# ============================================================


async def get_internal_user_id(
    service_key: str | None = Header(
        default=None,
        alias="X-CareerForge-Service-Key",
    ),
    user_id: str | None = Header(
        default=None,
        alias="X-CareerForge-User-ID",
    ),
) -> str:
    """
    Authenticate requests coming from Core Backend.

    The browser never calls this endpoint directly.

    Core Backend:
        1. authenticates the Cognito user
        2. determines the user's database UUID
        3. forwards that UUID to Agentic Service

    Agentic Service:
        1. validates the internal service key
        2. validates the user UUID
        3. uses that UUID for Agentic operations
    """

    if not service_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agentic service authentication required.",
        )

    if service_key != settings.internal_service_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid agentic service credentials.",
        )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is required.",
        )

    try:
        parsed_user_id = UUID(user_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID.",
        ) from exc

    return str(parsed_user_id)