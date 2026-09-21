from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentRequest:
    """
    Input received by the agent.

    user_id comes from authenticated application context.

    jd_id is optional.

    When jd_id is provided explicitly, it has priority.

    When jd_id is not provided, the agent can resolve a JD
    reference from the current session.
    """

    user_id: str
    message: str

    jd_id: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


@dataclass(slots=True)
class AgentResponse:
    """
    Final response returned by the agent.
    """

    message: str

    user_id: str

    # JD used as the active context for this response.
    jd_id: str | None = None

    retrieved_chunks: int = 0

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )