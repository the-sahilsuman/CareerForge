from fastapi import APIRouter

from app.api.routes.chat import (
    router as chat_router,
)
from app.api.routes.emails import (
    router as emails_router,
)


api_router = APIRouter(
    prefix="/api/v1",
)


api_router.include_router(
    chat_router,
)

api_router.include_router(
    emails_router,
)