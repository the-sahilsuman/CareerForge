from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class EventMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(default_factory=uuid4)
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    correlation_id: UUID | None = None
    causation_id: UUID | None = None
    source: str = "core-backend"
    version: int = 1


class BaseEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_type: str
    metadata: EventMetadata
    payload: dict[str, Any]