from __future__ import annotations

from abc import ABC, abstractmethod

from app.llm.factory import get_llm


class LLMProvider(ABC):
    """
    Provider-independent LLM interface used by the agent layer.
    """

    @abstractmethod
    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        raise NotImplementedError


class ConfiguredLLMProvider(LLMProvider):
    """
    Adapter between the agent layer and the provider abstraction.

    The actual provider is selected through LLM_PROVIDER.
    """

    def __init__(self) -> None:
        self.provider = get_llm()

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

        return await self.provider.ainvoke(messages)


def get_llm_provider() -> LLMProvider:
    """
    Return the configured LLM provider.

    Provider selection is controlled only through .env.
    """

    return ConfiguredLLMProvider()