from __future__ import annotations


SESSION_PREFIX = "careerforge:agentic:session"


def session_key(
    user_id: str,
) -> str:
    """
    Generate the Redis key for a user's active chat session.
    """

    if not user_id.strip():
        raise ValueError(
            "user_id cannot be empty."
        )

    return f"{SESSION_PREFIX}:{user_id}"