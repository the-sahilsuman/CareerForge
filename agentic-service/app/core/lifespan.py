from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.core.redis import (
    check_redis_connection,
    close_redis,
)
from app.db.session import (
    check_database_connection,
    close_database,
)
from app.workers.ingestion_worker import IngestionWorker


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle.

    Startup:
        1. Configure logging
        2. Verify PostgreSQL
        3. Verify Redis / ElastiCache
        4. Start SQS ingestion worker

    Shutdown:
        1. Stop SQS ingestion worker
        2. Close Redis
        3. Dispose PostgreSQL engine
    """

    setup_logging()

    logger.info(
        "Starting %s",
        settings.app_name,
    )

    ingestion_worker = None
    ingestion_worker_task = None

    try:
        # =====================================================
        # PostgreSQL
        # =====================================================

        logger.info(
            "Checking PostgreSQL connection..."
        )

        await check_database_connection()

        logger.info(
            "PostgreSQL connection successful."
        )

        # =====================================================
        # ElastiCache / Redis
        # =====================================================

        logger.info(
            "Checking ElastiCache / Redis connection..."
        )

        await check_redis_connection()

        logger.info(
            "ElastiCache / Redis connection successful."
        )

        # =====================================================
        # SQS INGESTION WORKER
        # =====================================================

        logger.info(
            "Starting ingestion worker..."
        )

        ingestion_worker = IngestionWorker()

        ingestion_worker_task = asyncio.create_task(
            asyncio.to_thread(
                ingestion_worker.run
            )
        )

        app.state.ingestion_worker = ingestion_worker
        app.state.ingestion_worker_task = (
            ingestion_worker_task
        )

        logger.info(
            "Ingestion worker started."
        )

        # =====================================================
        # Startup complete
        # =====================================================

        logger.info(
            "%s startup completed.",
            settings.app_name,
        )

        yield

    except Exception:
        logger.exception(
            "%s startup failed.",
            settings.app_name,
        )

        raise

    finally:

        # =====================================================
        # INGESTION WORKER
        # =====================================================

        if ingestion_worker is not None:
            logger.info(
                "Stopping ingestion worker..."
            )

            ingestion_worker.stop()

        if ingestion_worker_task is not None:
            try:
                await ingestion_worker_task
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.exception(
                    "Error while stopping ingestion worker."
                )

        logger.info(
            "Ingestion worker stopped."
        )

        # =====================================================
        # Redis
        # =====================================================

        try:
            await close_redis()
        except Exception:
            logger.exception(
                "Error while closing Redis connection."
            )

        # =====================================================
        # PostgreSQL
        # =====================================================

        try:
            await close_database()
        except Exception:
            logger.exception(
                "Error while closing PostgreSQL connection."
            )

        logger.info(
            "%s shutdown completed.",
            settings.app_name,
        )