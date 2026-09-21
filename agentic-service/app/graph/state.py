from __future__ import annotations

from typing import Any, TypedDict

from app.jd.models import (
    JDAnalysis,
    JDMatchResult,
)
from app.memory.models import (
    ChatSession,
    JDContext,
)
from app.retrieval.models import RetrievedChunk
from app.routing.models import RouteResult


class AgentGraphState(TypedDict, total=False):
    """
    Runtime state for one CareerForge agent execution.
    """

    # ========================================================
    # Request
    # ========================================================

    user_id: str

    message: str

    jd_id: str | None

    # ========================================================
    # Session
    # ========================================================

    session: ChatSession

    active_jd: JDContext | None

    # ========================================================
    # Routing
    # ========================================================

    route_result: RouteResult

    # ========================================================
    # Retrieval
    # ========================================================

    retrieved_chunks: list[RetrievedChunk]

    # ========================================================
    # JD Intelligence
    # ========================================================

    jd_analysis: JDAnalysis | None

    jd_match: JDMatchResult | None

    # ========================================================
    # JD Detection
    # ========================================================

    detected_jd_id: str | None

    detected_jd_title: str | None

    detected_jd_company: str | None

    detected_jd_confidence: float | None

    # ========================================================
    # Prompt Context
    # ========================================================

    conversation_context: str

    session_jds_context: str

    jd_context: str

    retrieved_context: str

    jd_intelligence_context: str

    # ========================================================
    # Email
    # ========================================================

    email_connection: dict[str, Any] | None

    email_credentials: Any | None

    email_draft: Any | None

    email_send_result: Any | None

    email_record_id: str | None

    resume_s3_url: str | None

    # ========================================================
    # Generation
    # ========================================================

    answer: str

    # ========================================================
    # Final metadata
    # ========================================================

    metadata: dict[str, Any]