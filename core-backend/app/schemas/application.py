from datetime import datetime
from uuid import UUID

from pydantic import Field, HttpUrl

from app.models.enums import ApplicationStatus
from app.schemas.common import BaseSchema


class ApplicationCreate(BaseSchema):
    company_name: str = Field(
        min_length=1,
        max_length=255,
    )

    job_title: str = Field(
        min_length=1,
        max_length=255,
    )

    job_url: HttpUrl | None = None

    job_description: str | None = Field(
        default=None,
        max_length=30000,
    )

    hr_email: str | None = Field(
        default=None,
        max_length=320,
    )

    status: ApplicationStatus = ApplicationStatus.TO_APPLY

    source: str | None = Field(
        default=None,
        max_length=100,
    )


class ApplicationUpdate(BaseSchema):
    company_name: str | None = Field(
        default=None,
        max_length=255,
    )

    job_title: str | None = Field(
        default=None,
        max_length=255,
    )

    job_url: HttpUrl | None = None

    job_description: str | None = Field(
        default=None,
        max_length=30000,
    )

    hr_email: str | None = Field(
        default=None,
        max_length=320,
    )

    status: ApplicationStatus | None = None

    source: str | None = Field(
        default=None,
        max_length=100,
    )


class ApplicationResponse(BaseSchema):
    id: UUID
    user_id: UUID

    company_name: str
    job_title: str

    job_url: HttpUrl | None
    job_description: str | None
    hr_email: str | None

    status: ApplicationStatus
    source: str | None

    applied_at: datetime | None
    created_at: datetime
    updated_at: datetime