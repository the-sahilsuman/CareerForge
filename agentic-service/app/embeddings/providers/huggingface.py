from __future__ import annotations

from huggingface_hub import InferenceClient

from app.core.config import settings
from app.embeddings.base import EmbeddingProvider


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """
    Hugging Face inference embedding provider.

    This provider is kept behind the same abstraction as
    Bedrock and Gemini.
    """

    def __init__(
        self,
        model: str | None = None,
    ) -> None:

        if not settings.huggingface_api_key:
            raise RuntimeError(
                "HUGGINGFACE_API_KEY is required "
                "for Hugging Face embeddings."
            )

        self.model = (
            model
            or settings.huggingface_embedding_model
        )

        if not self.model:
            raise RuntimeError(
                "HUGGINGFACE_EMBEDDING_MODEL_ID is required "
                "for Hugging Face embeddings."
            )

        self.client = InferenceClient(
            provider=settings.huggingface_embedding_provider,
            api_key=settings.huggingface_api_key,
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

        result = self.client.feature_extraction(
            text,
            model=self.model,
        )

        return self._normalise_result(result)

    @staticmethod
    def _normalise_result(
        result,
    ) -> list[float]:
        """
        Normalise Hugging Face output into a flat vector.
        """

        if hasattr(result, "tolist"):
            result = result.tolist()

        if not result:
            raise RuntimeError(
                "Hugging Face returned an empty embedding."
            )

        # Some models may return [[...]]
        if isinstance(result[0], list):
            if len(result) != 1:
                raise RuntimeError(
                    "Expected one embedding vector."
                )

            result = result[0]

        return [
            float(value)
            for value in result
        ]