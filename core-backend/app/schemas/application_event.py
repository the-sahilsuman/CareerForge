from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.models.enums import ApplicationStatus
from app.schemas.common import BaseSchema


class ApplicationEventResponse(BaseSchema):
    id: UUID
    application_id: UUID

    previous_status: ApplicationStatus | None
    new_status: ApplicationStatus

    source: str | None
    metadata: dict | None

    created_at: datetime
