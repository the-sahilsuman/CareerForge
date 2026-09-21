from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.lifespan import lifespan


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI agent service for CareerForge.",
    debug=settings.debug,
    lifespan=lifespan,
)


# ============================================================
# API v1
# ============================================================

app.include_router(
    api_router,
)


# ============================================================
# Health
# ============================================================


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Basic application health endpoint.

    Confirms that the FastAPI application process
    is running.
    """

    return {
        "status": "healthy",
        "service": "agentic-service",
    }


@app.get("/ready")
async def readiness_check() -> dict[str, str]:
    """
    Readiness endpoint.

    If the application reached this point after lifespan startup,
    required startup dependencies were successfully checked.
    """

    return {
        "status": "ready",
        "service": "agentic-service",
    }