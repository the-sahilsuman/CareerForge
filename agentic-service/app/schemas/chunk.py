from typing import Any

from pydantic import BaseModel, Field


class KnowledgeChunkData(BaseModel):
    """
    Represents one piece of user information that will be
    converted into an embedding and stored by Agentic Service.
    """

    user_id: str

    source_type: str
    source_id: str | None = None

    content: str

    metadata: dict[str, Any] = Field(default_factory=dict)