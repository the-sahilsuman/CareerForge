from typing import Any

from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.llm.base import BaseLLMProvider


class OpenAILLM(BaseLLMProvider):

    def __init__(self) -> None:

        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required for OpenAI."
            )

        kwargs = {
            "model": settings.openai_model_id,
            "api_key": settings.openai_api_key,
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens,
        }

        if settings.openai_base_url:
            kwargs["base_url"] = settings.openai_base_url

        self.llm = ChatOpenAI(**kwargs)

    async def ainvoke(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:

        response = await self.llm.ainvoke(
            messages,
            **kwargs,
        )

        return self._extract_content(response)

    async def astream(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ):

        async for chunk in self.llm.astream(
            messages,
            **kwargs,
        ):
            yield self._extract_content(chunk)

    @staticmethod
    def _extract_content(response: Any) -> str:

        content = getattr(
            response,
            "content",
            response,
        )

        if isinstance(content, str):
            return content.strip()

        return str(content)