from __future__ import annotations

import asyncio

from app.agent import (
    AgentRequest,
    agent_service,
)
from app.memory import session_manager


USER_ID = "section12-production-test-user"


async def main() -> None:

    print()
    print("=" * 70)
    print("SECTION 12 - PRODUCTION LANGGRAPH TEST")
    print("=" * 70)

    # ========================================================
    # Clean previous test session
    # ========================================================

    await session_manager.delete_session(
        USER_ID,
    )

    # ========================================================
    # Create session
    # ========================================================

    print()
    print("Creating session...")

    await session_manager.get_or_create(
        USER_ID,
    )

    # ========================================================
    # Add Google JD
    # ========================================================

    print("Adding Google JD...")

    await session_manager.add_jd(
        user_id=USER_ID,
        jd_id="google-backend",
        title="Backend Engineer",
        company="Google",
        description=(
            "Looking for a backend engineer with "
            "Python, FastAPI, PostgreSQL and AWS."
        ),
    )

    # ========================================================
    # Add Amazon JD
    # ========================================================

    print("Adding Amazon JD...")

    await session_manager.add_jd(
        user_id=USER_ID,
        jd_id="amazon-backend",
        title="Software Development Engineer",
        company="Amazon",
        description=(
            "Looking for a software engineer with "
            "Python, distributed systems, AWS and Docker."
        ),
    )

    # ========================================================
    # Google request
    # ========================================================

    google_question = (
        "Analyse the Google role and tell me "
        "which skills from my profile are relevant."
    )

    print()
    print("USER:")
    print(google_question)

    google_response = await agent_service.chat(
        AgentRequest(
            user_id=USER_ID,
            message=google_question,
        ),
    )

    print()
    print("GOOGLE RESPONSE:")
    print(google_response.message)

    print()
    print(
        "Active JD:",
        google_response.jd_id,
    )

    # ========================================================
    # Amazon switch
    # ========================================================

    amazon_question = (
        "Now switch to Amazon and tell me "
        "what skills I should highlight."
    )

    print()
    print("USER:")
    print(amazon_question)

    amazon_response = await agent_service.chat(
        AgentRequest(
            user_id=USER_ID,
            message=amazon_question,
        ),
    )

    print()
    print("AMAZON RESPONSE:")
    print(amazon_response.message)

    print()
    print(
        "Active JD:",
        amazon_response.jd_id,
    )

    # ========================================================
    # Follow-up using active JD
    # ========================================================

    follow_up = (
        "What am I missing for this role?"
    )

    print()
    print("USER:")
    print(follow_up)

    follow_up_response = await agent_service.chat(
        AgentRequest(
            user_id=USER_ID,
            message=follow_up,
        ),
    )

    print()
    print("FOLLOW-UP RESPONSE:")
    print(follow_up_response.message)

    print()
    print(
        "Active JD:",
        follow_up_response.jd_id,
    )

    # ========================================================
    # Verify session
    # ========================================================

    session = await session_manager.get_session(
        USER_ID,
    )

    print()
    print("=" * 70)
    print("SESSION VERIFICATION")
    print("=" * 70)

    print(
        "Messages:",
        len(session.messages),
    )

    print(
        "JDs:",
        list(session.jd_contexts.keys()),
    )

    print(
        "Active JD:",
        session.active_jd_id,
    )

    # ========================================================
    # Assertions
    # ========================================================

    assert len(session.jd_contexts) == 2

    assert session.active_jd_id == (
        "amazon-backend"
    )

    assert len(session.messages) == 6

    assert google_response.jd_id == (
        "google-backend"
    )

    assert amazon_response.jd_id == (
        "amazon-backend"
    )

    assert follow_up_response.jd_id == (
        "amazon-backend"
    )

    # ========================================================
    # Cleanup
    # ========================================================

    await session_manager.delete_session(
        USER_ID,
    )

    print()
    print("=" * 70)
    print("SECTION 12 PASSED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())