from app.clients.bedrock import bedrock_client
from app.core.config import settings
from app.embeddings.base import EmbeddingProvider


class BedrockEmbeddingProvider(EmbeddingProvider):
    """
    Amazon Bedrock embedding provider.

    Default model:
        amazon.titan-embed-text-v2:0
    """

    def __init__(
        self,
        model_id: str | None = None,
    ) -> None:

        self.model_id = (
            model_id
            or settings.bedrock_embedding_model_id
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

        return bedrock_client.generate_embedding(
            text=text,
            model_id=self.model_id,
        )