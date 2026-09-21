from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BucketStatus, BucketType


class BucketCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    type: BucketType = BucketType.TASK
    status: BucketStatus = BucketStatus.OPEN


class BucketUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    type: BucketType | None = None
    status: BucketStatus | None = None


class BucketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    description: str | None
    type: BucketType
    status: BucketStatus
    created_at: datetime
    updated_at: datetime