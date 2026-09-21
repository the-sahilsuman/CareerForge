from __future__ import annotations

from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings
from app.core.logging import get_logger
from app.vectorstore.base import VectorStore


logger = get_logger(__name__)


class S3VectorStore(VectorStore):
    """
    Amazon S3 Vectors implementation.

    Responsibilities:
        - Store vectors
        - Store vector metadata
        - Query nearest vectors
        - Delete vectors
        - Verify S3 Vectors connectivity

    This class intentionally hides the AWS SDK from the
    retrieval/ingestion layers.
    """

    def __init__(
        self,
        *,
        vector_bucket_name: str | None = None,
        index_name: str | None = None,
        index_arn: str | None = None,
    ) -> None:

        self.vector_bucket_name = (
            vector_bucket_name
            or settings.s3_vector_bucket_name
        )

        self.index_name = (
            index_name
            or settings.s3_vector_index_name
        )

        self.index_arn = (
            index_arn
            or settings.s3_vector_index_arn
        )

        self.client = boto3.client(
            "s3vectors",
            region_name=settings.aws_region,
        )

    # ========================================================
    # Configuration
    # ========================================================

    def _require_configuration(self) -> None:
        """
        Ensure the vector index has been configured.
        """

        if self.index_arn:
            return

        if not self.vector_bucket_name:
            raise RuntimeError(
                "S3 Vector bucket is not configured. "
                "Set S3_VECTOR_BUCKET_NAME."
            )

        if not self.index_name:
            raise RuntimeError(
                "S3 Vector index is not configured. "
                "Set S3_VECTOR_INDEX_NAME."
            )

    def _index_parameters(self) -> dict[str, str]:
        """
        Build parameters used by S3 Vectors APIs.
        """

        self._require_configuration()

        if self.index_arn:
            return {
                "indexArn": self.index_arn,
            }

        return {
            "vectorBucketName": self.vector_bucket_name,
            "indexName": self.index_name,
        }

    # ========================================================
    # Connection
    # ========================================================

    def check_connection(self) -> None:
        """
        Verify that the configured S3 Vector index is reachable.
        """

        self._require_configuration()

        try:
            self.client.get_index(
                **self._index_parameters(),
            )

            logger.info(
                "S3 Vector index connection successful."
            )

        except (BotoCoreError, ClientError):
            logger.exception(
                "S3 Vector index connection failed."
            )
            raise

    # ========================================================
    # Upsert
    # ========================================================

    def upsert(
        self,
        vectors: list[dict[str, Any]],
    ) -> None:
        """
        Store vectors in S3 Vectors.

        Expected vector structure:

        {
            "key": "resume:user123:chunk456",
            "data": {
                "float32": [0.1, 0.2, ...]
            },
            "metadata": {
                "user_id": "user123",
                "document_id": "resume456",
                "chunk_id": "chunk456"
            }
        }
        """

        if not vectors:
            return

        self._require_configuration()

        try:
            self.client.put_vectors(
                **self._index_parameters(),
                vectors=vectors,
            )

            logger.info(
                "Upserted %d vectors into S3 Vectors.",
                len(vectors),
            )

        except (BotoCoreError, ClientError):
            logger.exception(
                "Failed to upsert vectors into S3 Vectors."
            )
            raise

    # ========================================================
    # Query
    # ========================================================

    def query(
        self,
        vector: list[float],
        *,
        top_k: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search S3 Vectors using a query vector.
        """

        if not vector:
            raise ValueError(
                "Query vector cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        self._require_configuration()

        kwargs: dict[str, Any] = {
            **self._index_parameters(),
            "queryVector": {
                "float32": vector,
            },
            "topK": top_k,
            "returnDistance": True,
            "returnMetadata": True,
        }

        if filter:
            kwargs["filter"] = filter

        try:
            response = self.client.query_vectors(
                **kwargs,
            )

            return response.get(
                "vectors",
                [],
            )

        except (BotoCoreError, ClientError):
            logger.exception(
                "S3 Vector query failed."
            )
            raise

    # ========================================================
    # Delete
    # ========================================================

    def delete(
        self,
        keys: list[str],
    ) -> None:
        """
        Delete vectors using their keys.
        """

        if not keys:
            return

        self._require_configuration()

        try:
            self.client.delete_vectors(
                **self._index_parameters(),
                keys=keys,
            )

            logger.info(
                "Deleted %d vectors from S3 Vectors.",
                len(keys),
            )

        except (BotoCoreError, ClientError):
            logger.exception(
                "Failed to delete vectors from S3 Vectors."
            )
            raise

    # ========================================================
    # Get vectors
    # ========================================================

    def get(
        self,
        keys: list[str],
    ) -> list[dict[str, Any]]:
        """
        Retrieve vectors by key.
        """

        if not keys:
            return []

        self._require_configuration()

        try:
            response = self.client.get_vectors(
                **self._index_parameters(),
                keys=keys,
                returnData=True,
                returnMetadata=True,
            )

            return response.get(
                "vectors",
                [],
            )

        except (BotoCoreError, ClientError):
            logger.exception(
                "Failed to retrieve vectors."
            )
            raise
    

    def delete_document(
        self,
        *,
        document_id: str,
        user_id: str | None = None,
    ) -> None:

        self._require_configuration()

        next_token = None
        keys: list[str] = []

        while True:

            params = self._index_parameters()

            params["returnMetadata"] = True
            params["maxResults"] = 500

            if next_token:
                params["nextToken"] = next_token

            response = self.client.list_vectors(
                **params,
            )

            for vector in response.get(
                "vectors",
                [],
            ):
                metadata = vector.get(
                    "metadata",
                    {},
                )

                if metadata.get("document_id") != document_id:
                    continue

                if (
                    user_id is not None
                    and metadata.get("user_id") != user_id
                ):
                    continue

                key = vector.get("key")

                if key:
                    keys.append(key)

            next_token = response.get(
                "nextToken"
            )

            if not next_token:
                break

        if not keys:
            logger.info(
                "No vectors found for document=%s",
                document_id,
            )
            return

        for start in range(0, len(keys), 500):

            batch = keys[start:start + 500]

            self.client.delete_vectors(
                **self._index_parameters(),
                keys=batch,
            )

        logger.info(
            "Deleted %d vectors for document=%s",
            len(keys),
            document_id,
        )


s3_vector_store = S3VectorStore()