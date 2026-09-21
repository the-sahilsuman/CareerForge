from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class APIDataResponse(BaseModel, Generic[T]):
    data: T


class Pagination(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)


class APIListResponse(BaseModel, Generic[T]):
    data: list[T]
    pagination: Pagination


class APIError(BaseModel):
    code: str
    message: str
    request_id: str | None = None


class APIErrorResponse(BaseModel):
    error: APIError


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )