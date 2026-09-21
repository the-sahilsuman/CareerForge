from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """
    Common interface for all LLM providers.
    """

    @abstractmethod
    async def ainvoke(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        """Generate a complete LLM response."""
        raise NotImplementedError

    @abstractmethod
    async def astream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ):
        """Stream an LLM response."""
        raise NotImplementedError