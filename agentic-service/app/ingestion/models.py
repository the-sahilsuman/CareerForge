from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class IngestionMessage:
    """
    Normalised representation of an ingestion event.

    The queue layer converts the raw SQS message into this object.
    The rest of the ingestion pipeline doesn't need to know about
    SQS internals.
    """

    user_id: str
    document_id: str
    s3_key: str

    document_type: str = "resume"

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


@dataclass(slots=True)
class ParsedDocument:
    """
    Result of document parsing.
    """

    text: str
    source_key: str
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


@dataclass(slots=True)
class DocumentChunk:
    """
    One retrieval unit produced from a parsed document.
    """

    chunk_id: str
    text: str

    user_id: str
    document_id: str

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


@dataclass(slots=True)
class IngestionResult:
    """
    Final result of a successful ingestion operation.
    """

    user_id: str
    document_id: str
    chunks_created: int
    vectors_created: int