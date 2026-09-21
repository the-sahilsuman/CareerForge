from __future__ import annotations

import asyncio

from app.agent import (
    AgentRequest,
    agent_service,
)
from app.memory import session_manager


USER_ID = "section14-jd-routing-test-user"


async def show_state(
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
    print("ACTIVE JD RETURNED:")
    print(response.jd_id)

    print()
    print("METADATA:")
    print(response.metadata)


async def main() -> None:

    print()
    print("=" * 70)
    print("SECTION 14 - JD ROUTING REFINEMENT TEST")
    print("=" * 70)

    try:

        # ====================================================
        # 1. Create session
        # ====================================================

        await session_manager.get_or_create(
            USER_ID,
        )

        # ====================================================
        # 2. Add Google
        # ====================================================

        await session_manager.add_jd(
            user_id=USER_ID,
            jd_id="google-jd",
            title="Software Engineer",
            company="Google",
            description=(
                "Software Engineer role "
                "requiring Python and AWS."
            ),
        )

        # ====================================================
        # 3. Add Amazon
        # ====================================================

        await session_manager.add_jd(
            user_id=USER_ID,
            jd_id="amazon-jd",
            title="Backend Engineer",
            company="Amazon",
            description=(
                "Backend Engineer role "
                "requiring Python, FastAPI and AWS."
            ),
        )

        await show_state(
            "INITIAL STATE",
        )

        session = await session_manager.get_session(
            USER_ID,
        )

        assert (
            session.active_jd_id
            == "amazon-jd"
        )

        # ====================================================
        # 4. Explicit API JD
        # ====================================================

        await ask(
            "Analyse this role.",
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
        # 5. Natural company reference
        # ====================================================

        await ask(
            "Now go to Amazon.",
        )

        session = await session_manager.get_session(
            USER_ID,
        )

        assert (
            session.active_jd_id
            == "amazon-jd"
        )

        # ====================================================
        # 6. Active JD follow-up
        # ====================================================

        await ask(
            "What skills am I missing for this role?",
        )

        session = await session_manager.get_session(
            USER_ID,
        )

        assert (
            session.active_jd_id
            == "amazon-jd"
        )

        # ====================================================
        # 7. Relative switch
        # ====================================================

        await ask(
            "Switch to the other job.",
        )

        session = await session_manager.get_session(
            USER_ID,
        )

        assert (
            session.active_jd_id
            == "google-jd"
        )

        # ====================================================
        # 8. Return to Amazon
        # ====================================================

        await ask(
            "Go back to Amazon.",
        )

        session = await session_manager.get_session(
            USER_ID,
        )

        assert (
            session.active_jd_id
            == "amazon-jd"
        )

        # ====================================================
        # 9. Invalid explicit JD must fail
        # ====================================================

        try:

            await ask(
                "Analyse this.",
                jd_id="does-not-exist",
            )

        except KeyError:

            print()
            print(
                "Invalid JD correctly rejected."
            )

        else:

            raise AssertionError(
                "Invalid JD was accepted."
            )

        # ====================================================
        # 10. Final state
        # ====================================================

        await show_state(
            "FINAL STATE",
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

        print()
        print("=" * 70)
        print("SECTION 14 PASSED")
        print("=" * 70)

    finally:

        await session_manager.delete_session(
            USER_ID,
        )

        print()
        print(
            "Test session deleted."
        )


if __name__ == "__main__":
    asyncio.run(main())