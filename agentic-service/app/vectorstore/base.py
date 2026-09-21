from abc import ABC, abstractmethod
from typing import Any


class VectorStore(ABC):
    """
    Generic vector-store interface.

    Retrieval and ingestion depend on this abstraction.
    """

    @abstractmethod
    def upsert(
        self,
        vectors: list[dict[str, Any]],
    ) -> None:
        """
        Insert or replace vectors.
        """
        raise NotImplementedError

    @abstractmethod
    def query(
        self,
        vector: list[float],
        *,
        top_k: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for nearest vectors.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        keys: list[str],
    ) -> None:
        """
        Delete vectors by key.
        """
        raise NotImplementedError

    @abstractmethod
    def check_connection(self) -> None:
        """
        Verify vector-store connectivity.
        """
        raise NotImplementedError