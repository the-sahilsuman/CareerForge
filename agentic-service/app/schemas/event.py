from enum import Enum

from pydantic import BaseModel, Field


class EventOperation(str, Enum):
    """
    Operation that happened to a user data resource.
    """

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class EventResource(str, Enum):
    """
    User data resources that Agentic Service indexes.
    """

    RESUME = "resume"
    PROFILE = "profile"
    BIO = "bio"
    SKILLS = "skills"
    PROJECTS = "projects"
    EXPERIENCE = "experience"
    CERTIFICATIONS = "certifications"


class UserDataEvent(BaseModel):
    """
    Event received by Agentic Service when user data changes
    in the Core Backend.

    Agentic Service does not own this source data.
    The event only tells Agentic Service that the source changed.
    Agentic Service then retrieves the latest data and updates
    its knowledge index.
    """

    event_id: str = Field(..., description="Unique event identifier")

    user_id: str = Field(..., description="User who owns the changed data")

    resource: EventResource = Field(
        ...,
        description="Type of user data that changed",
    )

    operation: EventOperation = Field(
        ...,
        description="Operation performed on the resource",
    )

    resource_id: str | None = Field(
        default=None,
        description="ID of the changed resource when applicable",
    )

    timestamp: str = Field(
        ...,
        description="UTC timestamp when the event was generated",
    )

    metadata: dict | None = Field(
        default=None,
        description="Optional event metadata",
    )