from datetime import date
from uuid import UUID

from pydantic import Field

from app.schemas.common import BaseSchema


class EducationCreate(BaseSchema):
    institution: str = Field(min_length=1, max_length=255)
    degree: str = Field(min_length=1, max_length=150)
    field_of_study: str | None = Field(default=None, max_length=150)

    start_date: date | None = None
    end_date: date | None = None

    grade: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=2000)


class EducationUpdate(BaseSchema):
    institution: str | None = Field(default=None, max_length=255)
    degree: str | None = Field(default=None, max_length=150)
    field_of_study: str | None = Field(default=None, max_length=150)

    start_date: date | None = None
    end_date: date | None = None

    grade: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=2000)


class EducationResponse(BaseSchema):
    id: UUID
    user_id: UUID

    institution: str
    degree: str
    field_of_study: str | None

    start_date: date | None
    end_date: date | None

    grade: str | None
    description: str | None