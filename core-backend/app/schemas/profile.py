from uuid import UUID

from pydantic import EmailStr, Field, HttpUrl

from app.schemas.common import BaseSchema


class ProfileCreate(BaseSchema):

    first_name: str = Field(
        min_length=1,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        max_length=30,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    bio: str | None = Field(
        default=None,
        max_length=2500,
    )

    linkedin_url: HttpUrl | None = None

    github_url: HttpUrl | None = None

    portfolio_url: HttpUrl | None = None

    professional_email: EmailStr | None = None


class ProfileUpdate(BaseSchema):

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        max_length=30,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    bio: str | None = Field(
        default=None,
        max_length=2500,
    )

    linkedin_url: HttpUrl | None = None

    github_url: HttpUrl | None = None

    portfolio_url: HttpUrl | None = None

    professional_email: EmailStr | None = None


class ProfileResponse(BaseSchema):

    id: UUID

    user_id: UUID

    first_name: str

    last_name: str | None

    phone: str | None

    location: str | None

    bio: str | None

    linkedin_url: HttpUrl | None

    github_url: HttpUrl | None

    portfolio_url: HttpUrl | None

    professional_email: EmailStr | None = None