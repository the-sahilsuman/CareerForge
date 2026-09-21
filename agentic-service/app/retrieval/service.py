from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.embeddings import get_embedding_provider
from app.retrieval.models import RetrievedChunk
from app.vectorstore.s3_vectors import s3_vector_store


logger = get_logger(__name__)


EXPECTED_EMBEDDING_DIMENSION = 1024


class RetrievalService:
    """
    High-level retrieval service.

    Responsibilities:

        query text
            ↓
        embedding provider
            ↓
        S3 Vector Store
            ↓
        user/document isolation
            ↓
        normalised RetrievedChunk objects

    AgentService should communicate with this class rather
    than interacting with the vector store directly.
    """

    def __init__(
        self,
        vector_store=None,
        embedding_provider=None,
    ) -> None:

        self.vector_store = (
            vector_store
            if vector_store is not None
            else s3_vector_store
        )

        self.embedding_provider = (
            embedding_provider
            if embedding_provider is not None
            else get_embedding_provider()
        )

    # ========================================================
    # Vector Search
    # ========================================================

    async def search(
        self,
        *,
        user_id: str,
        query_vector: list[float],
        top_k: int = 5,
        document_id: str | None = None,
    ) -> list[RetrievedChunk]:
        """
        Search S3 Vectors using an already-generated embedding.
        """

        if not user_id:
            raise ValueError(
                "user_id is required."
            )

        if not query_vector:
            return []

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if len(query_vector) != EXPECTED_EMBEDDING_DIMENSION:
            raise ValueError(
                "Query embedding dimension mismatch: "
                f"expected {EXPECTED_EMBEDDING_DIMENSION}, "
                f"got {len(query_vector)}."
            )

        try:

            # Preferred S3 vector-store interface.
            results = self.vector_store.query(
                query_vector,
                top_k=top_k,
            )

        except AttributeError:

            # Compatibility with implementations exposing
            # an async/sync search() method instead.
            try:

                results = self.vector_store.search(
                    vector=query_vector,
                    top_k=top_k,
                )

            except AttributeError:

                raise RuntimeError(
                    "Vector store does not expose "
                    "query() or search()."
                )

        # Handle async search implementations.
        if hasattr(results, "__await__"):
            results = await results

        return self._normalise_results(
            results=results,
            user_id=user_id,
            document_id=document_id,
        )

    # ========================================================
    # Text Search
    # ========================================================

    async def search_text(
        self,
        *,
        user_id: str,
        query: str,
        top_k: int = 5,
        document_id: str | None = None,
    ) -> list[RetrievedChunk]:
        """
        Convert query text into an embedding and perform
        semantic vector search.
        """

        if not user_id:
            raise ValueError(
                "user_id is required."
            )

        if not query or not query.strip():
            return []

        query = query.strip()

        logger.debug(
            "Generating query embedding for user=%s",
            user_id,
        )

        vector = self.embedding_provider.embed_query(
            query,
        )

        if len(vector) != EXPECTED_EMBEDDING_DIMENSION:
            raise ValueError(
                "Query embedding dimension mismatch: "
                f"expected {EXPECTED_EMBEDDING_DIMENSION}, "
                f"got {len(vector)}."
            )

        return await self.search(
            user_id=user_id,
            query_vector=vector,
            top_k=top_k,
            document_id=document_id,
        )

    # ========================================================
    # Result Normalisation
    # ========================================================

    def _normalise_results(
        self,
        *,
        results: Any,
        user_id: str,
        document_id: str | None,
    ) -> list[RetrievedChunk]:
        """
        Convert raw vector-store results into RetrievedChunk
        objects while enforcing user/document isolation.
        """

        if not results:
            return []

        chunks: list[RetrievedChunk] = []

        for item in results:

            if not isinstance(item, dict):
                continue

            metadata = item.get(
                "metadata",
                {},
            )

            if not isinstance(metadata, dict):
                metadata = {}

            # ------------------------------------------------
            # User isolation
            # ------------------------------------------------

            result_user_id = metadata.get(
                "user_id"
            )

            if (
                result_user_id is not None
                and result_user_id != user_id
            ):
                continue

            # ------------------------------------------------
            # Document filtering
            # ------------------------------------------------

            result_document_id = metadata.get(
                "document_id"
            )

            if (
                document_id is not None
                and result_document_id is not None
                and result_document_id != document_id
            ):
                continue

            # ------------------------------------------------
            # Text
            # ------------------------------------------------

            text = metadata.get(
                "text"
            )

            if not text:
                text = item.get(
                    "text",
                    "",
                )

            if not text:
                continue

            # ------------------------------------------------
            # Key
            # ------------------------------------------------

            vector_key = (
                item.get("key")
                or item.get("id")
            )

            # ------------------------------------------------
            # Result
            # ------------------------------------------------

            chunks.append(
                RetrievedChunk(
                    text=str(text),
                    score=self._score(item),
                    vector_key=vector_key,
                    metadata=metadata,
                    source=metadata.get(
                        "source"
                    ),
                    document_id=result_document_id,
                )
            )

        logger.info(
            "Retrieved %d chunks for user=%s",
            len(chunks),
            user_id,
        )

        return chunks

    # ========================================================
    # Score
    # ========================================================

    @staticmethod
    def _score(
        item: dict[str, Any],
    ) -> float | None:
        """
        Extract a similarity/distance score from the
        vector-store response.
        """

        score = item.get("score")

        if score is None:
            score = item.get("distance")

        if score is None:
            return None

        try:
            return float(score)

        except (
            TypeError,
            ValueError,
        ):
            return None


retrieval_service = RetrievalService()