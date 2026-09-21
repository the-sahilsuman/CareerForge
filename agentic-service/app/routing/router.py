from __future__ import annotations

import json
from typing import Any

from app.agent.llm import LLMProvider
from app.core.logging import get_logger
from app.routing.models import (
    Intent,
    RouteResult,
)
from app.routing.prompts import (
    ROUTER_SYSTEM_PROMPT,
    build_router_prompt,
)


logger = get_logger(__name__)


class IntentRouter:

    def __init__(
        self,
        llm: LLMProvider,
    ) -> None:

        self.llm = llm

    async def route(
        self,
        *,
        message: str,
        active_jd_id: str | None = None,
        available_jds: list[dict[str, Any]] | None = None,
    ) -> RouteResult:

        prompt = build_router_prompt(
            message=message,
            active_jd_id=active_jd_id,
            available_jds=available_jds,
        )

        raw = await self.llm.generate(
            system_prompt=ROUTER_SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        valid_jd_ids = {
            jd["jd_id"]
            for jd in (
                available_jds or []
            )
            if jd.get("jd_id")
        }

        return self._parse(
            raw,
            valid_jd_ids=valid_jd_ids,
        )

    def _parse(
        self,
        raw: str,
        *,
        valid_jd_ids: set[str] | None = None,
    ) -> RouteResult:

        try:

            cleaned = raw.strip()

            if cleaned.startswith(
                "```"
            ):

                cleaned = (
                    cleaned
                    .replace(
                        "```json",
                        "",
                    )
                    .replace(
                        "```",
                        "",
                    )
                    .strip()
                )

            data = json.loads(
                cleaned,
            )

            result = RouteResult.model_validate(
                data,
            )

            # ------------------------------------------------
            # Never allow the router to invent a JD.
            # ------------------------------------------------

            if (
                result.jd_id is not None
                and valid_jd_ids is not None
                and result.jd_id not in valid_jd_ids
            ):

                logger.warning(
                    "Router returned invalid JD ID: %s",
                    result.jd_id,
                )

                result.jd_id = None

                result.reasoning = (
                    "Router selected an unavailable JD; "
                    "JD selection was discarded."
                )

            return result

        except Exception as exc:

            logger.warning(
                "Failed to parse router response: %s",
                exc,
            )

            return RouteResult(
                intent=Intent.UNKNOWN,
                confidence=0.0,
                reasoning=(
                    "Router response could not be parsed."
                ),
            )