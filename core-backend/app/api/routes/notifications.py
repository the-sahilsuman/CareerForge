from uuid import UUID

from fastapi import APIRouter

from app.schemas.notification import NotificationResponse

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=list[NotificationResponse],
)
async def list_notifications():
    raise NotImplementedError


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
async def mark_notification_read(
    notification_id: UUID,
):
    raise NotImplementedError


@router.patch(
    "/read-all",
)
async def mark_all_notifications_read():
    raise NotImplementedError