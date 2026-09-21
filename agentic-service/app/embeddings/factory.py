from functools import lru_cache

from app.core.config import settings

from app.embeddings.base import EmbeddingProvider

from app.embeddings.providers.bedrock import (
    BedrockEmbeddingProvider,
)

from app.embeddings.providers.gemini import (
    GeminiEmbeddingProvider,
)

from app.embeddings.providers.huggingface import (
    HuggingFaceEmbeddingProvider,
)

from app.embeddings.providers.openrouter import (
    OpenRouterEmbeddingProvider,
)


@lru_cache
def get_embedding_provider(
    provider: str | None = None,
) -> EmbeddingProvider:
    """
    Return the configured embedding provider.

    Supported:
        bedrock
        gemini
        huggingface
        openrouter
    """

    selected = (
        provider
        or settings.embedding_provider
    ).lower()

    if selected == "bedrock":

        return BedrockEmbeddingProvider()

    if selected == "gemini":

        return GeminiEmbeddingProvider()

    if selected in {
        "huggingface",
        "hugging_face",
        "hf",
    }:

        return HuggingFaceEmbeddingProvider()

    if selected in {
        "openrouter",
        "open_router",
    }:

        return OpenRouterEmbeddingProvider()

    raise ValueError(
        "Unsupported embedding provider: "
        f"{selected}"
    )