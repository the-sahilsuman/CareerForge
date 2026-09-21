from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RetrievedChunk:
    """
    A single result returned by vector retrieval.
    """

    text: str

    score: float | None = None

    vector_key: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    source: str | None = None

    document_id: str | None = None