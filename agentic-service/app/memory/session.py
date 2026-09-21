from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.memory.keys import session_key
from app.memory.models import (
    ChatMessage,
    ChatSession,
    JDContext,
)
from app.memory.redis_client import redis_client


logger = get_logger(__name__)


class SessionManager:
    """
    Manage temporary agentic chat sessions.

    Session properties:

    - One active session per user.
    - Multiple JDs can exist in one session.
    - Messages are temporary.
    - Session expires after configured TTL.
    - Every meaningful interaction refreshes the TTL.

    Multi-JD behaviour:

        One user
            |
            v
        One session
            |
            +---- JD-1
            +---- JD-2
            +---- JD-3
            |
            v
        active_jd_id
    """

    # ========================================================
    # Serialisation
    # ========================================================

    @staticmethod
    def _serialize(
        session: ChatSession,
    ) -> str:

        payload: dict[str, Any] = {
            "user_id": session.user_id,
            "messages": [
                message.to_dict()
                for message in session.messages
            ],
            "jd_contexts": {
                jd_id: jd.to_dict()
                for jd_id, jd in session.jd_contexts.items()
            },
            "active_jd_id": session.active_jd_id,
            "metadata": session.metadata,
        }

        return json.dumps(
            payload,
            ensure_ascii=False,
        )

    @staticmethod
    def _deserialize(
        value: str,
    ) -> ChatSession:

        payload = json.loads(value)

        messages = [
            ChatMessage(**message)
            for message in payload.get(
                "messages",
                [],
            )
        ]

        jd_contexts = {
            jd_id: JDContext(**jd)
            for jd_id, jd in payload.get(
                "jd_contexts",
                {},
            ).items()
        }

        return ChatSession(
            user_id=payload["user_id"],
            messages=messages,
            jd_contexts=jd_contexts,
            active_jd_id=payload.get(
                "active_jd_id"
            ),
            metadata=payload.get(
                "metadata",
                {},
            ),
        )

    # ========================================================
    # Create / get
    # ========================================================

    async def get_or_create(
        self,
        user_id: str,
    ) -> ChatSession:

        if not user_id.strip():
            raise ValueError(
                "user_id cannot be empty."
            )

        key = session_key(user_id)

        raw = await redis_client.get(key)

        if raw is None:

            session = ChatSession(
                user_id=user_id,
            )

            await self._save(
                session,
            )

            logger.info(
                "Created new chat session for user=%s",
                user_id,
            )

            return session

        session = self._deserialize(raw)

        await redis_client.expire(
            key,
            settings.redis_session_ttl,
        )

        return session

    # ========================================================
    # Save
    # ========================================================

    async def _save(
        self,
        session: ChatSession,
    ) -> None:

        key = session_key(
            session.user_id,
        )

        await redis_client.set(
            key,
            self._serialize(session),
            ttl=settings.redis_session_ttl,
        )

    # ========================================================
    # Messages
    # ========================================================

    async def add_message(
        self,
        *,
        user_id: str,
        role: str,
        content: str,
    ) -> ChatSession:

        if role not in {
            "system",
            "user",
            "assistant",
        }:
            raise ValueError(
                f"Invalid message role: {role}"
            )

        if not content.strip():
            raise ValueError(
                "Message content cannot be empty."
            )

        session = await self.get_or_create(
            user_id,
        )

        session.messages.append(
            ChatMessage(
                role=role,
                content=content,
                timestamp=(
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                ),
            )
        )

        await self._save(
            session,
        )

        return session

    async def get_messages(
        self,
        user_id: str,
    ) -> list[ChatMessage]:

        session = await self.get_or_create(
            user_id,
        )

        return session.messages

    # ========================================================
    # JD management
    # ========================================================

    async def add_jd(
        self,
        *,
        user_id: str,
        jd_id: str,
        title: str | None = None,
        company: str | None = None,
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ChatSession:

        if not jd_id.strip():
            raise ValueError(
                "jd_id cannot be empty."
            )

        session = await self.get_or_create(
            user_id,
        )

        session.jd_contexts[jd_id] = JDContext(
            jd_id=jd_id,
            title=title,
            company=company,
            description=description,
            metadata=metadata or {},
        )

        # Newly added JD becomes active.
        session.active_jd_id = jd_id

        await self._save(
            session,
        )

        logger.info(
            "Added JD %s to user session %s",
            jd_id,
            user_id,
        )

        return session

    async def get_jd(
        self,
        *,
        user_id: str,
        jd_id: str,
    ) -> JDContext | None:

        session = await self.get_or_create(
            user_id,
        )

        return session.jd_contexts.get(
            jd_id,
        )

    async def get_jds(
        self,
        user_id: str,
    ) -> dict[str, JDContext]:

        session = await self.get_or_create(
            user_id,
        )

        return dict(
            session.jd_contexts
        )

    async def set_active_jd(
        self,
        *,
        user_id: str,
        jd_id: str,
    ) -> ChatSession:

        session = await self.get_or_create(
            user_id,
        )

        if jd_id not in session.jd_contexts:
            raise KeyError(
                f"JD not found in session: {jd_id}"
            )

        session.active_jd_id = jd_id

        await self._save(
            session,
        )

        logger.info(
            "Active JD changed: user=%s jd=%s",
            user_id,
            jd_id,
        )

        return session

    async def get_active_jd(
        self,
        user_id: str,
    ) -> JDContext | None:

        session = await self.get_or_create(
            user_id,
        )

        if not session.active_jd_id:
            return None

        return session.jd_contexts.get(
            session.active_jd_id
        )

    # ========================================================
    # JD reference resolution
    # ========================================================

    @staticmethod
    def _normalise(
        value: str | None,
    ) -> str:

        if not value:
            return ""

        return " ".join(
            value.lower()
            .strip()
            .split()
        )

    def resolve_jd_reference(
        self,
        session: ChatSession,
        reference: str,
    ) -> JDContext | None:
        """
        Resolve a human JD reference against the JDs stored
        inside the current session.

        Matching order:

        1. Exact JD ID
        2. Exact company
        3. Exact title
        4. Company/title contained in reference
        5. JD ID contained in reference

        Returns None when the reference is ambiguous or
        cannot be resolved.
        """

        reference_normalised = self._normalise(
            reference
        )

        if not reference_normalised:
            return None

        # ----------------------------------------------------
        # Exact JD ID
        # ----------------------------------------------------

        for jd_id, jd in session.jd_contexts.items():

            if self._normalise(jd_id) == reference_normalised:
                return jd

        # ----------------------------------------------------
        # Exact company/title
        # ----------------------------------------------------

        exact_matches: list[JDContext] = []

        for jd in session.jd_contexts.values():

            company = self._normalise(
                jd.company
            )

            title = self._normalise(
                jd.title
            )

            if reference_normalised in {
                company,
                title,
            }:
                exact_matches.append(jd)

        if len(exact_matches) == 1:
            return exact_matches[0]

        # ----------------------------------------------------
        # Partial company/title/JD ID match
        # ----------------------------------------------------

        candidates: list[JDContext] = []

        for jd_id, jd in session.jd_contexts.items():

            searchable_values = [
                self._normalise(jd_id),
                self._normalise(jd.company),
                self._normalise(jd.title),
            ]

            for value in searchable_values:

                if not value:
                    continue

                if (
                    value in reference_normalised
                    or reference_normalised in value
                ):
                    candidates.append(jd)
                    break

        # Only resolve when unambiguous.
        unique_ids = {
            jd.jd_id
            for jd in candidates
        }

        if len(unique_ids) == 1:
            return candidates[0]

        return None

    # ========================================================
    # Session information
    # ========================================================

    async def get_session(
        self,
        user_id: str,
    ) -> ChatSession:

        return await self.get_or_create(
            user_id
        )

    async def delete_session(
        self,
        user_id: str,
    ) -> None:

        key = session_key(
            user_id,
        )

        await redis_client.delete(
            key,
        )

        logger.info(
            "Deleted chat session for user=%s",
            user_id,
        )

    async def get_ttl(
        self,
        user_id: str,
    ) -> int:

        return await redis_client.ttl(
            session_key(user_id)
        )


session_manager = SessionManager()