from redis.asyncio import Redis

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


redis_client = Redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    ssl_cert_reqs=None if not settings.redis_ca_cert else "required",
    ssl_ca_certs=settings.redis_ca_cert,
    health_check_interval=30,
)


async def check_redis_connection() -> None:
    """
    Verify that Redis / ElastiCache is reachable.
    """

    await redis_client.ping()


async def get_redis() -> Redis:
    """
    Return the shared Redis client.
    """

    return redis_client


async def close_redis() -> None:
    """
    Close the shared Redis connection.
    """

    await redis_client.aclose()

    logger.info("Redis connection closed.")