from __future__ import annotations

import httpx

from app.core.config import settings
from app.embeddings.base import EmbeddingProvider


class OpenRouterEmbeddingProvider(
    EmbeddingProvider
):
    """
    OpenRouter embedding provider.

    Model:
        liquid/lfm-2.5-embedding-350m:free

    Native dimension:
        1014
    """

    def __init__(
        self,
        model: str | None = None,
    ) -> None:

        if not settings.openrouter_api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is required "
                "for OpenRouter embeddings."
            )

        self.model = (
            model
            or settings.openrouter_embedding_model
        )

        self.output_dimension = (
            settings.openrouter_embedding_dimensions
        )

        if self.output_dimension != 1024:
            raise RuntimeError(
                "Nemotron 3 Embed 1B requires "
                "2048-dimensional embeddings."
            )

        self.base_url = (
            settings.openrouter_base_url
            .rstrip("/")
        )

        self.headers = {
            "Authorization": (
                f"Bearer "
                f"{settings.openrouter_api_key}"
            ),
            "Content-Type": "application/json",
        }

    def embed_text(
        self,
        text: str,
        *,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[float]:

        if not text.strip():
            raise ValueError(
                "Cannot generate embedding "
                "for empty text."
            )

        input_type = self._map_task_type(
            task_type
        )

        payload = {
            "model": self.model,
            "input": text,
            "encoding_format": "float",
            "input_type": input_type,
        }

        response = httpx.post(
            f"{self.base_url}/embeddings",
            headers=self.headers,
            json=payload,
            timeout=120.0,
        )

        if response.status_code >= 400:

            raise RuntimeError(
                "OpenRouter embedding request failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        data = response.json()

        embeddings = data.get(
            "data"
        )

        if not embeddings:

            raise RuntimeError(
                "OpenRouter returned no embeddings."
            )

        vector = embeddings[0].get(
            "embedding"
        )

        if not vector:

            raise RuntimeError(
                "OpenRouter returned an empty "
                "embedding vector."
            )

        vector = [
            float(value)
            for value in vector
        ]

        if len(vector) != (
            self.output_dimension
        ):

            raise RuntimeError(
                "OpenRouter returned an unexpected "
                "embedding dimension: "
                f"expected "
                f"{self.output_dimension}, "
                f"got {len(vector)}."
            )

        return vector

    @staticmethod
    def _map_task_type(
        task_type: str,
    ) -> str:

        if task_type == (
            "RETRIEVAL_QUERY"
        ):
            return "search_query"

        return "search_document"