from typing import Any

from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.llm.base import BaseLLMProvider


class HuggingFaceLLM(BaseLLMProvider):
    """
    Hugging Face Inference Providers LLM.

    Uses the OpenAI-compatible Hugging Face router.

    Provider/model selection is controlled by environment variables.
    """

    def __init__(self) -> None:

        if not settings.huggingface_api_key:
            raise RuntimeError(
                "HUGGINGFACE_API_KEY is required "
                "for Hugging Face."
            )

        if not settings.huggingface_llm_model_id:
            raise RuntimeError(
                "HUGGINGFACE_LLM_MODEL_ID is required "
                "for Hugging Face."
            )

        self.llm = ChatOpenAI(
            model=settings.huggingface_llm_model_id,
            api_key=settings.huggingface_api_key,
            base_url=settings.huggingface_base_url,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
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

        content = getattr(
            response,
            "content",
            response,
        )

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):

            parts: list[str] = []

            for block in content:

                if isinstance(block, dict):

                    text = block.get("text")

                    if text:
                        parts.append(str(text))

            return "".join(parts).strip()

        return str(content).strip()