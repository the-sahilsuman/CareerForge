from __future__ import annotations

from typing import Any

from app.agent.llm import get_llm_provider
from app.core.logging import get_logger
from app.routing.models import (
    Intent,
    RouteResult,
)
from app.routing.router import IntentRouter


logger = get_logger(__name__)


class RoutingService:

    def __init__(self) -> None:

        llm = get_llm_provider()

        self.router = IntentRouter(
            llm=llm,
        )

    async def route(
        self,
        *,
        message: str,
        active_jd_id: str | None = None,
        available_jds: list[dict[str, Any]] | None = None,
    ) -> RouteResult:

        if not message.strip():

            return RouteResult(
                intent=Intent.UNKNOWN,
                confidence=0.0,
            )

        result = await self.router.route(
            message=message,
            active_jd_id=active_jd_id,
            available_jds=available_jds,
        )

        logger.info(
            "Intent routed: intent=%s confidence=%s jd=%s",
            result.intent,
            result.confidence,
            result.jd_id,
        )

        return result


routing_service = RoutingService()