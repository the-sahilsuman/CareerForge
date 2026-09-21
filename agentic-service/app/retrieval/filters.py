from __future__ import annotations

from typing import Any

from app.retrieval.models import RetrievalQuery


def build_vector_filter(
    request: RetrievalQuery,
) -> dict[str, Any]:
    """
    Build the S3 Vector metadata filter.

    user_id is ALWAYS mandatory.

    Additional filters are optional.
    """

    if not request.user_id.strip():
        raise ValueError(
            "user_id is required for retrieval."
        )

    vector_filter: dict[str, Any] = {
        "user_id": request.user_id,
    }

    if request.document_id:
        vector_filter["document_id"] = (
            request.document_id
        )

    if request.document_type:
        vector_filter["document_type"] = (
            request.document_type
        )

    if request.metadata_filter:
        vector_filter.update(
            request.metadata_filter
        )

    return vector_filter