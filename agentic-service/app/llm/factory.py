from functools import lru_cache

from app.core.config import settings

from app.llm.base import BaseLLMProvider

from app.llm.providers import (
    BedrockLLM,
    GeminiLLM,
    HuggingFaceLLM,
    OpenAILLM,
    OpenRouterLLM,
)


class LLMFactory:
    """
    Creates the configured LLM provider.
    """

    @staticmethod
    def create(
        provider: str | None = None,
    ) -> BaseLLMProvider:

        selected_provider = (
            provider or settings.llm_provider
        ).lower()

        if selected_provider == "bedrock":
            return BedrockLLM()

        if selected_provider == "gemini":
            return GeminiLLM()

        if selected_provider == "openai":
            return OpenAILLM()

        if selected_provider in {
            "huggingface",
            "hugging_face",
            "hf",
        }:
            return HuggingFaceLLM()

        if selected_provider in {
            "openrouter",
            "open_router",
        }:
            return OpenRouterLLM()

        raise ValueError(
            f"Unsupported LLM provider: "
            f"{selected_provider}. "
            "Supported providers: "
            "bedrock, gemini, openai, "
            "huggingface, openrouter."
        )


@lru_cache(maxsize=1)
def get_llm() -> BaseLLMProvider:

    return LLMFactory.create()