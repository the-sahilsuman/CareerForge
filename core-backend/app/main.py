from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import AppError
from app.core.logging import configure_logging
from app.db.session import (
    check_database_connection,
    close_database,
)
from app.middleware.error_handler import (
    app_error_handler,
    unexpected_error_handler,
)
from app.middleware.request_id import RequestIDMiddleware
from app.workers.outbox_worker import OutboxWorker


@asynccontextmanager
async def lifespan(app: FastAPI):

    configure_logging()

    # --------------------------------------------------------
    # DATABASE STARTUP CHECK
    # --------------------------------------------------------

    await check_database_connection()

    # --------------------------------------------------------
    # OUTBOX WORKER
    # --------------------------------------------------------

    outbox_worker = OutboxWorker()

    logger = __import__("logging").getLogger(__name__)

    logger.info(
        "Starting Outbox Worker..."
    )

    outbox_task = asyncio.create_task(
        outbox_worker.run()
    )

    app.state.outbox_worker = outbox_worker
    app.state.outbox_worker_task = outbox_task

    logger.info(
        "Outbox Worker started."
    )

    # --------------------------------------------------------
    # Application is now allowed to start serving traffic.
    # --------------------------------------------------------

    try:
        yield

    finally:

        # ----------------------------------------------------
        # OUTBOX WORKER SHUTDOWN
        # ----------------------------------------------------

        logger.info(
            "Stopping Outbox Worker..."
        )

        outbox_task.cancel()

        try:
            await outbox_task
        except asyncio.CancelledError:
            pass

        logger.info(
            "Outbox Worker stopped."
        )

        # ----------------------------------------------------
        # DATABASE SHUTDOWN
        # ----------------------------------------------------

        await close_database()


app = FastAPI(
    title="CareerForge Core Backend",
    description="Core business API for CareerForge.",
    version="0.1.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

cors_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Application middleware
# ---------------------------------------------------------------------------

app.add_middleware(RequestIDMiddleware)


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

app.add_exception_handler(
    AppError,
    app_error_handler,
)

app.add_exception_handler(
    Exception,
    unexpected_error_handler,
)


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

app.include_router(
    api_router,
    prefix="/api/v1",
)


# ---------------------------------------------------------------------------
# Health / root endpoint
# ---------------------------------------------------------------------------

@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "running",
    }