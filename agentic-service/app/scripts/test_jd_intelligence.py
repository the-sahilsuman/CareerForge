from __future__ import annotations

import asyncio

from app.agent import (
    AgentRequest,
    agent_service,
)
from app.memory import session_manager


USER_ID = "section17-jd-intelligence-test"


async def main() -> None:

    print()
    print("=" * 70)
    print("SECTION 17 - JD INTELLIGENCE TEST")
    print("=" * 70)

    await session_manager.delete_session(
        USER_ID,
    )

    try:

        # ====================================================
        # Create session
        # ====================================================

        print()
        print("Creating session...")

        await session_manager.get_or_create(
            USER_ID,
        )

        # ====================================================
        # Google JD
        # ====================================================

        print("Adding Google JD...")

        await session_manager.add_jd(
            user_id=USER_ID,
            jd_id="google-backend",
            title="Backend Engineer",
            company="Google",
            description="""
We are looking for a Backend Engineer.

Required skills:
Python, FastAPI, PostgreSQL, Docker and AWS.

Preferred:
Kubernetes and distributed systems.

Responsibilities:
Build backend APIs, maintain services and improve
backend reliability.
""".strip(),
        )

        # ====================================================
        # Amazon JD
        # ====================================================

        print("Adding Amazon JD...")

        await session_manager.add_jd(
            user_id=USER_ID,
            jd_id="amazon-backend",
            title="Software Development Engineer",
            company="Amazon",
            description="""
We are looking for a Software Development Engineer.

Required skills:
Python, AWS, Docker and distributed systems.

Preferred:
Kubernetes and PostgreSQL.

Responsibilities:
Build scalable backend services and distributed systems.
""".strip(),
        )

        # ====================================================
        # Verify active JD
        # ====================================================

        session = await session_manager.get_session(
            USER_ID,
        )

        assert session.active_jd_id == (
            "amazon-backend"
        )

        assert set(
            session.jd_contexts.keys()
        ) == {
            "google-backend",
            "amazon-backend",
        }

        print()
        print(
            "Active JD:",
            session.active_jd_id,
        )

        # ====================================================
        # Ask JD match question
        # ====================================================

        print()
        print("Running JD intelligence...")

        response = await agent_service.chat(
            AgentRequest(
                user_id=USER_ID,
                message=(
                    "How well does my profile match "
                    "this Amazon role and what skills "
                    "am I missing?"
                ),
            )
        )

        print()
        print("RESPONSE")
        print("-" * 70)

        print(
            response.message,
        )

        print()
        print("METADATA")
        print("-" * 70)

        print(
            response.metadata,
        )

        # ====================================================
        # Verify active JD
        # ====================================================

        assert response.jd_id == (
            "amazon-backend"
        )

        # ====================================================
        # Verify JD intelligence metadata
        # ====================================================

        assert (
            "jd_intelligence"
            in response.metadata
        )

        assert (
            "jd_match"
            in response.metadata
        )

        jd_intelligence = response.metadata[
            "jd_intelligence"
        ]

        jd_match = response.metadata[
            "jd_match"
        ]

        assert isinstance(
            jd_intelligence[
                "required_skills"
            ],
            list,
        )

        assert isinstance(
            jd_match[
                "matched_skills"
            ],
            list,
        )

        assert isinstance(
            jd_match[
                "missing_required_skills"
            ],
            list,
        )

        # ====================================================
        # Switch to Google
        # ====================================================

        print()
        print("Switching to Google...")

        google_response = (
            await agent_service.chat(
                AgentRequest(
                    user_id=USER_ID,
                    message=(
                        "Now analyse the Google role."
                    ),
                )
            )
        )

        print()
        print(
            "Google active JD:",
            google_response.jd_id,
        )

        assert google_response.jd_id == (
            "google-backend"
        )

        assert (
            "jd_intelligence"
            in google_response.metadata
        )

        # ====================================================
        # Verify same session
        # ====================================================

        session = await session_manager.get_session(
            USER_ID,
        )

        assert session.active_jd_id == (
            "google-backend"
        )

        assert set(
            session.jd_contexts.keys()
        ) == {
            "google-backend",
            "amazon-backend",
        }

        # Two requests:
        #
        # Amazon:
        #   user + assistant = 2
        #
        # Google:
        #   user + assistant = 2
        #
        # Total = 4

        assert len(
            session.messages
        ) == 4

        # ====================================================
        # Final
        # ====================================================

        print()
        print("=" * 70)
        print("SECTION 17 PASSED")
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