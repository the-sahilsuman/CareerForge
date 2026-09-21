from datetime import date
from uuid import UUID

from pydantic import Field, HttpUrl

from app.schemas.common import BaseSchema


class ProjectCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    technologies: list[str] = Field(
        default_factory=list,
        max_length=30,
    )

    github_url: HttpUrl | None = None
    live_url: HttpUrl | None = None

    start_date: date | None = None
    end_date: date | None = None


class ProjectUpdate(BaseSchema):
    name: str | None = Field(default=None, max_length=255)

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    technologies: list[str] | None = Field(
        default=None,
        max_length=30,
    )

    github_url: HttpUrl | None = None
    live_url: HttpUrl | None = None

    start_date: date | None = None
    end_date: date | None = None


class ProjectResponse(BaseSchema):
    id: UUID
    user_id: UUID

    name: str
    description: str | None

    technologies: list[str]

    github_url: HttpUrl | None
    live_url: HttpUrl | None

    start_date: date | None
    end_date: date | None