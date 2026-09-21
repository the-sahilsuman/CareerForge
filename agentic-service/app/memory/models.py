from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ChatMessage:
    """
    One message in the temporary conversation history.
    """

    role: str
    content: str
    timestamp: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class JDContext:
    """
    Temporary context for one job description.

    Multiple JDContext objects can exist inside the same
    user session.
    """

    jd_id: str

    title: str | None = None
    company: str | None = None
    description: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ChatSession:
    """
    Temporary user chat session.

    One user has one active session.

    Multiple JDs can exist inside that session.
    """

    user_id: str

    messages: list[ChatMessage] = field(
        default_factory=list,
    )

    jd_contexts: dict[str, JDContext] = field(
        default_factory=dict,
    )

    active_jd_id: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )