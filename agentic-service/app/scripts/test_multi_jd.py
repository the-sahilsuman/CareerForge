import asyncio

from app.agent import (
    AgentRequest,
    agent_service,
)
from app.memory import session_manager


USER_ID = "section11-multi-jd-test-user"


async def print_session_state(
    label: str,
) -> None:

    session = await session_manager.get_session(
        USER_ID,
    )

    print()
    print("-" * 70)
    print(label)
    print("-" * 70)

    print(
        "Active JD:",
        session.active_jd_id,
    )

    print(
        "Available JDs:",
        list(
            session.jd_contexts.keys()
        ),
    )

    print(
        "Messages:",
        len(session.messages),
    )


async def ask(
    message: str,
    jd_id: str | None = None,
) -> None:

    print()
    print("USER:")
    print(message)

    response = await agent_service.chat(
        AgentRequest(
            user_id=USER_ID,
            message=message,
            jd_id=jd_id,
        )
    )

    print()
    print("ASSISTANT:")
    print(response.message)

    print()
    print(
        "Active JD returned:",
        response.jd_id,
    )

    print(
        "Metadata:",
        response.metadata,
    )


async def main() -> None:

    print()
    print("=" * 70)
    print("SECTION 11 - MULTI-JD CONVERSATION TEST")
    print("=" * 70)

    try:

        # ====================================================
        # 1. Create session
        # ====================================================

        print()
        print("Creating session...")

        await session_manager.get_or_create(
            USER_ID,
        )

        # ====================================================
        # 2. Add Google JD
        # ====================================================

        print("Adding Google JD...")

        await session_manager.add_jd(
            user_id=USER_ID,
            jd_id="google-jd",
            title="Software Engineer",
            company="Google",
            description=(
                "Looking for a Software Engineer "
                "with Python, distributed systems, "
                "AWS and strong backend engineering."
            ),
        )

        # ====================================================
        # 3. Add Amazon JD
        # ====================================================

        print("Adding Amazon JD...")

        await session_manager.add_jd(
            user_id=USER_ID,
            jd_id="amazon-jd",
            title="Backend Engineer",
            company="Amazon",
            description=(
                "Looking for a Backend Engineer "
                "with Python, FastAPI, PostgreSQL, "
                "AWS and Docker."
            ),
        )

        # Newly added Amazon JD should be active.
        await print_session_state(
            "AFTER ADDING TWO JDs"
        )

        session = await session_manager.get_session(
            USER_ID,
        )

        assert set(
            session.jd_contexts.keys()
        ) == {
            "google-jd",
            "amazon-jd",
        }

        assert (
            session.active_jd_id
            == "amazon-jd"
        )

        # ====================================================
        # 4. Explicitly switch to Google
        # ====================================================

        await ask(
            "Analyse the Google role.",
            jd_id="google-jd",
        )

        session = await session_manager.get_session(
            USER_ID,
        )

        assert (
            session.active_jd_id
            == "google-jd"
        )

        # ====================================================
        # 5. Explicitly switch to Amazon
        # ====================================================

        await ask(
            "Now analyse the Amazon role.",
            jd_id="amazon-jd",
        )

        session = await session_manager.get_session(
            USER_ID,
        )

        assert (
            session.active_jd_id
            == "amazon-jd"
        )

        # ====================================================
        # 6. Ask follow-up without JD ID
        # ====================================================

        await ask(
            "What skills am I missing for this role?"
        )

        session = await session_manager.get_session(
            USER_ID,
        )

        assert (
            session.active_jd_id
            == "amazon-jd"
        )

        # ====================================================
        # 7. Natural-language switch
        # ====================================================

        await ask(
            "Go back to Google."
        )

        session = await session_manager.get_session(
            USER_ID,
        )

        assert (
            session.active_jd_id
            == "google-jd"
        )

        # ====================================================
        # 8. Compare Google with Amazon
        # ====================================================

        await ask(
            "Compare this with Amazon."
        )

        session = await session_manager.get_session(
            USER_ID,
        )

        # The reference to Amazon should resolve the
        # Amazon JD while the conversation history still
        # contains the Google discussion.
        assert (
            session.active_jd_id
            == "amazon-jd"
        )

        # ====================================================
        # 9. Verify persistence
        # ====================================================

        await print_session_state(
            "FINAL SESSION STATE"
        )

        session = await session_manager.get_session(
            USER_ID,
        )

        assert len(
            session.messages
        ) >= 10

        assert set(
            session.jd_contexts.keys()
        ) == {
            "google-jd",
            "amazon-jd",
        }

        print()
        print("=" * 70)
        print("SECTION 11 PASSED")
        print("=" * 70)

    finally:

        print()
        print("Cleaning up test session...")

        await session_manager.delete_session(
            USER_ID,
        )

        print(
            "Test session deleted."
        )


if __name__ == "__main__":
    asyncio.run(main())