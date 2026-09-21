from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Intent(StrEnum):
    PROFILE = "profile"
    RESUME = "resume"
    JD_ANALYSIS = "jd_analysis"
    JD_MATCH = "jd_match"
    JD_SWITCH = "jd_switch"

    EMAIL_DRAFT = "email_draft"
    EMAIL_SEND = "email_send"

    GENERAL_CAREER = "general_career"
    UNKNOWN = "unknown"


class RouteResult(BaseModel):
    intent: Intent = Field(
        default=Intent.UNKNOWN
    )

    jd_id: str | None = None

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    reasoning: str | None = None