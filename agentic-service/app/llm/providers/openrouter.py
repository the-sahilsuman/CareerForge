from typing import Any

from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.llm.base import BaseLLMProvider


class OpenRouterLLM(BaseLLMProvider):
    """
    OpenRouter LLM provider.

    OpenRouter exposes an OpenAI-compatible API,
    so ChatOpenAI can be used with a custom base URL.
    """

    def __init__(self) -> None:

        if not settings.openrouter_api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is required "
                "for OpenRouter."
            )

        self.llm = ChatOpenAI(
            model=settings.openrouter_llm_model,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            default_headers={
                "X-Title": "CareerForge Agentic Service",
            },
        )

    async def ainvoke(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:

        response = await self.llm.ainvoke(
            messages,
            **kwargs,
        )

        return self._extract_content(
            response
        )

    async def astream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ):

        async for chunk in self.llm.astream(
            messages,
            **kwargs,
        ):
            yield self._extract_content(
                chunk
            )

    @staticmethod
    def _extract_content(
        response: Any,
    ) -> str:

        content = getattr(
            response,
            "content",
            response,
        )

        if isinstance(
            content,
            str,
        ):
            return content

        if isinstance(
            content,
            list,
        ):
            parts: list[str] = []

            for block in content:

                if isinstance(
                    block,
                    dict,
                ):
                    text = block.get(
                        "text",
                        "",
                    )

                    if text:
                        parts.append(
                            str(text)
                        )

            return "".join(parts)

        return str(content)