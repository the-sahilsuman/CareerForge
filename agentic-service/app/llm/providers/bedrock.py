from typing import Any

from langchain_aws import ChatBedrockConverse

from app.core.config import settings
from app.llm.base import BaseLLMProvider


class BedrockLLM(BaseLLMProvider):

    def __init__(self) -> None:
        self.llm = ChatBedrockConverse(
            model=settings.bedrock_model_id,
            region_name=settings.bedrock_aws_region,
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
        content = getattr(response, "content", response)

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            return "".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict)
            )

        return str(content)