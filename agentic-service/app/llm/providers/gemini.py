from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.llm.base import BaseLLMProvider


class GeminiLLM(BaseLLMProvider):

    def __init__(self) -> None:
        if not settings.google_api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is required for Gemini."
            )

        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model_id,
            google_api_key=settings.google_api_key,
            temperature=settings.llm_temperature,
            max_output_tokens=settings.llm_max_tokens,
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
        content = getattr(response, "content", response)

        if isinstance(content, str):
            return content

        return str(content)