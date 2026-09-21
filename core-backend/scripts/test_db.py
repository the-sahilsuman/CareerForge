import asyncio

from sqlalchemy import text

from app.db.session import engine


async def test_connection():
    try:
        async with engine.connect() as connection:
            result = await connection.execute(
                text("SELECT version();")
            )

            version = result.scalar()

            print("✅ Database connection successful")
            print(f"PostgreSQL: {version}")

    except Exception as exc:
        print("❌ Database connection failed")
        print(f"{type(exc).__name__}: {exc}")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection())