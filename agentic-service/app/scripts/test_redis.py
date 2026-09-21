import asyncio

import redis.asyncio as redis

from app.core.config import settings


async def main() -> None:

    print("Redis URL:", settings.redis_url)

    client = redis.from_url(
        settings.redis_url,
        decode_responses=True,
        # ssl_cert_reqs=None if not settings.redis_ca_cert else "required",
        # ssl_ca_certs=settings.redis_ca_cert,
        socket_connect_timeout=5,
    )

    try:
        print("Pinging Redis...")

        result = await client.ping()

        print("Redis PING:", result)

        await client.set(
            "careerforge:test",
            "hello",
            ex=60,
        )

        value = await client.get(
            "careerforge:test"
        )

        print("Redis GET:", value)

    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())