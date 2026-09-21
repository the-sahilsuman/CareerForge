from __future__ import annotations

from app.core.logging import get_logger
from app.embeddings import get_embedding_provider
from app.retrieval.filters import build_vector_filter
from app.retrieval.models import (
    RetrievedChunk,
    RetrievalQuery,
)
from app.vectorstore import s3_vector_store


logger = get_logger(__name__)


class VectorRetriever:
    """
    Semantic retrieval over S3 Vectors.

    Responsibilities:

        query text
            ↓
        embedding
            ↓
        metadata filter
            ↓
        S3 Vector search
            ↓
        normalised chunks
    """

    def __init__(self) -> None:

        self.embedding_provider = (
            get_embedding_provider()
        )

    def retrieve(
        self,
        request: RetrievalQuery,
    ) -> list[RetrievedChunk]:

        if not request.query.strip():
            raise ValueError(
                "Retrieval query cannot be empty."
            )

        if request.top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        # ----------------------------------------------------
        # Query embedding
        # ----------------------------------------------------

        query_vector = (
            self.embedding_provider.embed_query(
                request.query,
            )
        )

        # ----------------------------------------------------
        # User/document filters
        # ----------------------------------------------------

        vector_filter = build_vector_filter(
            request,
        )

        # ----------------------------------------------------
        # Vector search
        # ----------------------------------------------------

        results = s3_vector_store.query(
            query_vector,
            top_k=request.top_k,
            filter=vector_filter,
        )

        # ----------------------------------------------------
        # Normalise S3 Vector response
        # ----------------------------------------------------

        chunks: list[RetrievedChunk] = []

        for result in results:

            metadata = result.get(
                "metadata",
                {},
            )

            chunks.append(
                RetrievedChunk(
                    key=result["key"],
                    text=str(
                        metadata.get(
                            "text",
                            "",
                        )
                    ),
                    distance=result.get(
                        "distance"
                    ),
                    score=self._distance_to_score(
                        result.get("distance")
                    ),
                    user_id=metadata.get(
                        "user_id"
                    ),
                    document_id=metadata.get(
                        "document_id"
                    ),
                    chunk_id=metadata.get(
                        "chunk_id"
                    ),
                    metadata=metadata,
                )
            )

        logger.info(
            "Retrieved %d chunks for user=%s",
            len(chunks),
            request.user_id,
        )

        return chunks

    @staticmethod
    def _distance_to_score(
        distance: float | None,
    ) -> float | None:
        """
        Convert distance into a simple similarity-like score.

        This is intentionally kept simple for now.

        Later we can use the exact metric configured on the
        S3 Vector index and define a proper scoring strategy.
        """

        if distance is None:
            return None

        return 1.0 / (1.0 + distance)


vector_retriever = VectorRetriever()