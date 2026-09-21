from __future__ import annotations

import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class RedisClient:
    """
    Shared async Redis client.

    Redis/ElastiCache is used for temporary agent session state.
    """

    def __init__(self) -> None:

        if not settings.redis_url:
            raise RuntimeError(
                "REDIS_URL is not configured."
            )

        self.client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            ssl_cert_reqs="none"
        )

    async def ping(self) -> bool:

        result = await self.client.ping()

        return bool(result)

    async def get(
        self,
        key: str,
    ) -> str | None:

        return await self.client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        *,
        ttl: int,
    ) -> None:

        await self.client.set(
            key,
            value,
            ex=ttl,
        )

    async def delete(
        self,
        key: str,
    ) -> None:

        await self.client.delete(key)

    async def expire(
        self,
        key: str,
        ttl: int,
    ) -> None:

        await self.client.expire(
            key,
            ttl,
        )

    async def ttl(
        self,
        key: str,
    ) -> int:

        return await self.client.ttl(key)

    async def close(self) -> None:

        await self.client.aclose()


redis_client = RedisClient()