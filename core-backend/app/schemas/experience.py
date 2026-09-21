from datetime import date
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.common import BaseSchema


class ExperienceCreate(BaseSchema):
    company: str = Field(min_length=1, max_length=255)
    job_title: str = Field(min_length=1, max_length=150)

    employment_type: str | None = Field(
        default=None,
        max_length=50,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    start_date: date | None = None
    end_date: date | None = None

    is_current: bool = False

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError(
                    "end_date cannot be earlier than start_date"
                )

        if self.is_current and self.end_date is not None:
            raise ValueError(
                "Current experience cannot have an end_date"
            )

        return self


class ExperienceUpdate(BaseSchema):
    company: str | None = Field(default=None, max_length=255)
    job_title: str | None = Field(default=None, max_length=150)

    employment_type: str | None = Field(
        default=None,
        max_length=50,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None

    description: str | None = Field(
        default=None,
        max_length=5000,
    )


class ExperienceResponse(BaseSchema):
    id: UUID
    user_id: UUID

    company: str
    job_title: str
    employment_type: str | None
    location: str | None

    start_date: date | None
    end_date: date | None

    is_current: bool
    description: str | None