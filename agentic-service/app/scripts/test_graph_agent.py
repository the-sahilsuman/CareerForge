from __future__ import annotations

import asyncio

from app.agent import (
    AgentRequest,
    agent_service,
)
from app.memory import session_manager


USER_ID = "section10-test-user"


async def main() -> None:

    print()
    print("=" * 70)
    print("SECTION 10 - LANGGRAPH AGENT TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Create session
    # --------------------------------------------------------

    print()
    print("Creating session...")

    await session_manager.get_or_create(
        USER_ID,
    )

    # --------------------------------------------------------
    # Add JD
    # --------------------------------------------------------

    print("Adding JD...")

    await session_manager.add_jd(
        user_id=USER_ID,
        jd_id="section10-jd",
        title="Python Backend Engineer",
        company="CareerForge Test",
        description=(
            "Looking for a Python backend engineer "
            "with FastAPI, PostgreSQL, AWS and Docker."
        ),
    )

    # --------------------------------------------------------
    # First message
    # --------------------------------------------------------

    question = (
        "What skills from my resume are relevant "
        "to this backend engineering role?"
    )

    print()
    print("USER:")
    print(question)

    response = await agent_service.chat(
        AgentRequest(
            user_id=USER_ID,
            message=question,
            jd_id="section10-jd",
        )
    )

    print()
    print("=" * 70)
    print("FIRST RESPONSE")
    print("=" * 70)

    print(response.message)

    print()
    print(
        "Retrieved chunks:",
        response.retrieved_chunks,
    )

    print(
        "JD:",
        response.jd_id,
    )

    # --------------------------------------------------------
    # Second message
    # --------------------------------------------------------

    follow_up = (
        "Which of those skills should I highlight "
        "most strongly in my application?"
    )

    print()
    print("USER:")
    print(follow_up)

    response_2 = await agent_service.chat(
        AgentRequest(
            user_id=USER_ID,
            message=follow_up,
            jd_id="section10-jd",
        )
    )

    print()
    print("=" * 70)
    print("FOLLOW-UP RESPONSE")
    print("=" * 70)

    print(response_2.message)

    print()
    print(
        "Retrieved chunks:",
        response_2.retrieved_chunks,
    )

    # --------------------------------------------------------
    # Verify session
    # --------------------------------------------------------

    session = await session_manager.get_session(
        USER_ID,
    )

    print()
    print(
        "Stored messages:",
        len(session.messages),
    )

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    await session_manager.delete_session(
        USER_ID,
    )

    print()
    print("=" * 70)
    print("SECTION 10 PASSED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())