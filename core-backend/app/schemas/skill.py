from uuid import UUID

from pydantic import Field

from app.schemas.common import BaseSchema


class SkillCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=100)
    category: str | None = Field(default=None, max_length=100)
    proficiency: str | None = Field(default=None, max_length=50)
    years_of_experience: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class SkillUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, max_length=100)
    proficiency: str | None = Field(default=None, max_length=50)
    years_of_experience: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class SkillResponse(BaseSchema):
    id: UUID
    user_id: UUID
    name: str
    category: str | None
    proficiency: str | None
    years_of_experience: int | None