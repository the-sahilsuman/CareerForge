from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings


class AgenticServiceError(Exception):
    """
    Raised when Core Backend cannot communicate
    with Agentic Service.
    """


class AgenticServiceClient:

    def __init__(self) -> None:
        self.base_url = (
            settings.agentic_service_url.rstrip("/")
        )

    def _headers(
        self,
        user_id: str,
    ) -> dict[str, str]:

        return {
            "X-CareerForge-Service-Key": (
                settings.agentic_internal_service_key
            ),
            "X-CareerForge-User-ID": user_id,
        }

    async def chat(
        self,
        *,
        user_id: str,
        message: str,
        jd_id: str | None = None,
    ) -> dict[str, Any]:

        payload = {
            "message": message,
            "jd_id": jd_id,
        }

        try:

            async with httpx.AsyncClient(
                timeout=90.0,
            ) as client:

                response = await client.post(
                    f"{self.base_url}/api/v1/chat",
                    json=payload,
                    headers=self._headers(
                        user_id,
                    ),
                )

        except httpx.RequestError as exc:

            raise AgenticServiceError(
                "Unable to reach Agentic Service."
            ) from exc

        if response.status_code >= 400:

            try:
                detail = response.json().get(
                    "detail",
                    "Agentic request failed.",
                )

            except Exception:
                detail = (
                    "Agentic request failed."
                )

            raise AgenticServiceError(
                str(detail)
            )

        return response.json()

    async def get_chat_history(
        self,
        *,
        user_id: str,
    ) -> dict[str, Any]:

        try:

            async with httpx.AsyncClient(
                timeout=30.0,
            ) as client:

                response = await client.get(
                    f"{self.base_url}/api/v1/chat/history",
                    headers=self._headers(
                        user_id,
                    ),
                )

        except httpx.RequestError as exc:

            raise AgenticServiceError(
                "Unable to reach Agentic Service."
            ) from exc

        if response.status_code >= 400:

            raise AgenticServiceError(
                "Unable to load chat history."
            )

        return response.json()

    async def get_email_records(
        self,
        *,
        user_id: str,
    ) -> list[dict[str, Any]]:

        try:

            async with httpx.AsyncClient(
                timeout=30.0,
            ) as client:

                response = await client.get(
                    f"{self.base_url}/api/v1/emails",
                    headers=self._headers(
                        user_id,
                    ),
                )

        except httpx.RequestError as exc:

            raise AgenticServiceError(
                "Unable to reach Agentic Service."
            ) from exc

        if response.status_code >= 400:

            raise AgenticServiceError(
                "Unable to load email history."
            )

        return response.json()


agentic_service_client = (
    AgenticServiceClient()
)