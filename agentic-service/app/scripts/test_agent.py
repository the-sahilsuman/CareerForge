import asyncio

from app.agent import AgentRequest, agent_service
from app.memory import session_manager


USER_ID = "section7-test-user"


async def setup() -> None:

    await session_manager.add_jd(
        user_id=USER_ID,
        jd_id="jd-001",
        title="Backend Engineer",
        company="Test Company",
        description=(
            "Looking for a Python backend engineer "
            "with FastAPI, PostgreSQL, AWS and Docker."
        ),
    )


async def main() -> None:

    print("\nSetting up test session...")

    await setup()

    print("Sending message...\n")

    response = await agent_service.chat(
        AgentRequest(
            user_id=USER_ID,
            message=(
                "What skills from my profile are "
                "relevant to this job?"
            ),
            jd_id="jd-001",
        )
    )

    print(
        "========== AGENT RESPONSE =========="
    )

    print(
        "User:",
        response.user_id,
    )

    print(
        "JD:",
        response.jd_id,
    )

    print(
        "Retrieved chunks:",
        response.retrieved_chunks,
    )

    print()
    print(response.message)

    print(
        "\n====================================="
    )

    # --------------------------------------------------------
    # Verify conversation was stored
    # --------------------------------------------------------

    session = (
        await session_manager.get_session(
            USER_ID,
        )
    )

    print(
        "\nMessages stored:",
        len(session.messages),
    )

    for message in session.messages:
        print(
            f"{message.role}: "
            f"{message.content}"
        )

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    await session_manager.delete_session(
        USER_ID,
    )

    print(
        "\nTest session deleted."
    )


if __name__ == "__main__":
    asyncio.run(main())