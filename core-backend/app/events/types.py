from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.events.base import BaseEvent, EventMetadata


class ResumeUploadedPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    resume_id: UUID
    resume_version_id: UUID
    s3_key: str
    file_name: str
    content_type: str


class ResumeUploadedEvent(BaseEvent):
    event_type: str = "resume.uploaded"
    payload: ResumeUploadedPayload
    metadata: EventMetadata


class ResumeProcessingCompletedPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    resume_id: UUID
    resume_version_id: UUID
    vector_document_count: int = Field(ge=0)


class ResumeProcessingCompletedEvent(BaseEvent):
    event_type: str = "resume.processing.completed"
    payload: ResumeProcessingCompletedPayload
    metadata: EventMetadata


class ResumeProcessingFailedPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    resume_id: UUID
    resume_version_id: UUID
    error_code: str
    error_message: str


class ResumeProcessingFailedEvent(BaseEvent):
    event_type: str = "resume.processing.failed"
    payload: ResumeProcessingFailedPayload
    metadata: EventMetadata


class ResumeReplacedPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    resume_id: UUID
    old_version_id: UUID | None
    new_version_id: UUID


class ResumeReplacedEvent(BaseEvent):
    event_type: str = "resume.replaced"
    payload: ResumeReplacedPayload
    metadata: EventMetadata


class ProfileUpdatedPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    profile_id: UUID
    changed_fields: list[str]


class ProfileUpdatedEvent(BaseEvent):
    event_type: str = "profile.updated"
    payload: ProfileUpdatedPayload
    metadata: EventMetadata