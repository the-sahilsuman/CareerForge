from __future__ import annotations

from app.agent.models import AgentRequest
from app.memory.models import (
    ChatMessage,
    ChatSession,
    JDContext,
)
from app.retrieval.models import RetrievedChunk


class ContextBuilder:
    """
    Converts internal application objects into safe,
    compact LLM context.

    Multi-JD aware:

        One session
            |
            +---- active JD
            +---- other JDs
            |
            v
        LLM context
    """

    # ========================================================
    # Conversation
    # ========================================================

    def build_conversation(
        self,
        messages: list[ChatMessage],
        *,
        max_messages: int = 20,
    ) -> str:

        if not messages:
            return ""

        recent_messages = messages[
            -max_messages:
        ]

        lines: list[str] = []

        for message in recent_messages:

            role = message.role.upper()

            lines.append(
                f"{role}: {message.content}"
            )

        return "\n".join(lines)

    # ========================================================
    # Single JD
    # ========================================================

    def build_jd(
        self,
        jd: JDContext | None,
    ) -> str:

        if jd is None:
            return ""

        parts: list[str] = [
            f"JD ID: {jd.jd_id}"
        ]

        if jd.title:
            parts.append(
                f"Title: {jd.title}"
            )

        if jd.company:
            parts.append(
                f"Company: {jd.company}"
            )

        if jd.description:
            parts.append(
                f"Description:\n{jd.description}"
            )

        return "\n".join(parts)

    # ========================================================
    # All session JDs
    # ========================================================

    def build_session_jds(
        self,
        session: ChatSession,
        *,
        max_description_chars: int = 2500,
    ) -> str:

        if not session.jd_contexts:
            return ""

        sections: list[str] = []

        for jd_id, jd in session.jd_contexts.items():

            active_marker = (
                "ACTIVE"
                if jd_id == session.active_jd_id
                else "AVAILABLE"
            )

            lines = [
                f"[{active_marker} JD]",
                f"JD ID: {jd.jd_id}",
            ]

            if jd.title:
                lines.append(
                    f"Title: {jd.title}"
                )

            if jd.company:
                lines.append(
                    f"Company: {jd.company}"
                )

            if jd.description:
                description = jd.description[
                    :max_description_chars
                ]

                lines.append(
                    f"Description:\n{description}"
                )

            sections.append(
                "\n".join(lines)
            )

        return "\n\n".join(sections)

    # ========================================================
    # Retrieved context
    # ========================================================

    def build_retrieved_context(
        self,
        chunks: list[RetrievedChunk],
        *,
        max_chunks: int = 5,
        max_chars_per_chunk: int = 3000,
    ) -> str:

        if not chunks:
            return ""

        sections: list[str] = []

        for index, chunk in enumerate(
            chunks[:max_chunks],
            start=1,
        ):

            text = chunk.text.strip()

            if not text:
                continue

            text = text[
                :max_chars_per_chunk
            ]

            source = (
                chunk.source
                or "unknown"
            )

            score = (
                f"{chunk.score:.4f}"
                if chunk.score is not None
                else "unknown"
            )

            sections.append(
                f"""
[Retrieved Context {index}]
Source: {source}
Score: {score}

{text}
""".strip()
            )

        return "\n\n".join(sections)

    # ========================================================
    # Complete context
    # ========================================================

    def build(
        self,
        *,
        request: AgentRequest,
        messages: list[ChatMessage],
        session: ChatSession,
        active_jd: JDContext | None,
        chunks: list[RetrievedChunk],
    ) -> dict[str, str]:

        return {
            "conversation": (
                self.build_conversation(
                    messages,
                )
            ),
            "active_jd": (
                self.build_jd(
                    active_jd,
                )
            ),
            "session_jds": (
                self.build_session_jds(
                    session,
                )
            ),
            "retrieved_context": (
                self.build_retrieved_context(
                    chunks,
                )
            ),
        }


context_builder = ContextBuilder()