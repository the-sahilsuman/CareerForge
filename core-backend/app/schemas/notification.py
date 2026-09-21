from datetime import datetime
from uuid import UUID

from app.schemas.common import BaseSchema


class NotificationResponse(BaseSchema):
    id: UUID
    type: str
    title: str
    message: str

    is_read: bool

    metadata: dict | None

    created_at: datetime
    read_at: datetime | None