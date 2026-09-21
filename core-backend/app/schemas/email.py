from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from app.models.enums import (
    EmailConnectionStatus,
    EmailProvider,
    EmailStatus,
)
from app.schemas.common import BaseSchema


class EmailConnectionResponse(BaseSchema):

    id: UUID

    provider: EmailProvider

    email_address: EmailStr

    status: EmailConnectionStatus

    expires_at: datetime | None

    created_at: datetime


class EmailResponse(BaseSchema):

    id: UUID

    application_id: UUID | None

    connection_id: UUID | None

    from_email: EmailStr

    to_email: EmailStr

    subject: str

    body: str

    provider: EmailProvider

    provider_message_id: str | None

    status: EmailStatus

    sent_at: datetime | None

    created_at: datetime