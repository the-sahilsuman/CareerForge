from __future__ import annotations

from google import genai
from google.genai import types

from app.core.config import settings
from app.embeddings.base import EmbeddingProvider


class GeminiEmbeddingProvider(EmbeddingProvider):
    """
    Google Gemini embedding provider.

    The Gemini embedding model can return different output
    dimensions. The dimension must match the configured
    S3 Vector index.

    Current architecture:
        Gemini → 1024 dimensions → S3 Vectors
    """

    def __init__(
        self,
        model: str | None = None,
    ) -> None:

        if not settings.google_api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is required for Gemini embeddings."
            )

        self.model = (
            model
            or settings.gemini_embedding_model
        )

        self.output_dimension = (
            settings.embedding_dimensions
        )

        if not self.output_dimension:
            raise RuntimeError(
                "EMBEDDING_DIMENSIONS must be configured."
            )

        self.client = genai.Client(
            api_key=settings.google_api_key,
        )

    def embed_text(
        self,
        text: str,
        *,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[float]:

        if not text.strip():
            raise ValueError(
                "Cannot generate embedding for empty text."
            )

        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=self.output_dimension,
            ),
        )

        if not response.embeddings:
            raise RuntimeError(
                "Gemini returned no embedding."
            )

        values = response.embeddings[0].values

        if values is None:
            raise RuntimeError(
                "Gemini returned an empty embedding."
            )

        vector = list(values)

        if len(vector) != self.output_dimension:
            raise RuntimeError(
                "Gemini returned an unexpected embedding "
                f"dimension: expected {self.output_dimension}, "
                f"got {len(vector)}."
            )

        return vector