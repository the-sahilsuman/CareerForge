from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel, Field

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
)
from app.services.agentic import (
    AgenticServiceError,
    agentic_service_client,
)


router = APIRouter(
    prefix="/agentic",
    tags=["Agentic Service"],
)


class AgenticChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )

    jd_id: str | None = Field(
        default=None,
        max_length=255,
    )


@router.post(
    "/chat",
)
async def chat(
    payload: AgenticChatRequest,
    current_user: CurrentUser = Depends(
        get_current_user,
    ),
) -> dict[str, Any]:

    try:

        return await agentic_service_client.chat(
            user_id=str(current_user.id),
            message=payload.message,
            jd_id=payload.jd_id,
        )

    except AgenticServiceError as exc:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get(
    "/chat/history",
)
async def get_chat_history(
    current_user: CurrentUser = Depends(
        get_current_user,
    ),
) -> dict[str, Any]:

    try:

        return await agentic_service_client.get_chat_history(
            user_id=str(current_user.id),
        )

    except AgenticServiceError as exc:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get(
    "/emails",
)
async def get_email_records(
    current_user: CurrentUser = Depends(
        get_current_user,
    ),
) -> list[dict[str, Any]]:

    try:

        return await agentic_service_client.get_email_records(
            user_id=str(current_user.id),
        )

    except AgenticServiceError as exc:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc