from datetime import date
from uuid import UUID

from pydantic import Field, HttpUrl

from app.schemas.common import BaseSchema


class CertificationCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    issuer: str = Field(min_length=1, max_length=255)

    credential_id: str | None = Field(
        default=None,
        max_length=255,
    )

    credential_url: HttpUrl | None = None

    issue_date: date | None = None
    expiry_date: date | None = None


class CertificationUpdate(BaseSchema):
    name: str | None = Field(default=None, max_length=255)
    issuer: str | None = Field(default=None, max_length=255)

    credential_id: str | None = Field(
        default=None,
        max_length=255,
    )

    credential_url: HttpUrl | None = None

    issue_date: date | None = None
    expiry_date: date | None = None


class CertificationResponse(BaseSchema):
    id: UUID
    user_id: UUID

    name: str
    issuer: str

    credential_id: str | None
    credential_url: HttpUrl | None

    issue_date: date | None
    expiry_date: date | None