from typing import Any

from pydantic import BaseModel, Field


class UserDataSnapshot(BaseModel):
    """
    Normalized snapshot of the user's data fetched from
    the Core Backend public schema.

    This is the input to the ingestion pipeline.
    """

    user_id: str

    user: dict[str, Any] = Field(default_factory=dict)
    profile: list[dict[str, Any]] = Field(default_factory=list)
    skills: list[dict[str, Any]] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    certifications: list[dict[str, Any]] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    resumes: list[dict[str, Any]] = Field(default_factory=list)