from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ingestion-service",
    }


@router.get("/ready")
async def ready() -> dict[str, str]:
    return {
        "status": "ready",
        "service": "ingestion-service",
    }