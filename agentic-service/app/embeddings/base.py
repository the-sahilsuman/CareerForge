from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):

    @abstractmethod
    def embed_text(
        self,
        text: str,
        *,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[float]:
        raise NotImplementedError

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        return [
            self.embed_text(
                text,
                task_type="RETRIEVAL_DOCUMENT",
            )
            for text in texts
        ]

    def embed_query(
        self,
        text: str,
    ) -> list[float]:

        return self.embed_text(
            text,
            task_type="RETRIEVAL_QUERY",
        )