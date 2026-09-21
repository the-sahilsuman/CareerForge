from __future__ import annotations

import asyncio

from app.agent import (
    AgentRequest,
    agent_service,
)
from app.graph import (
    agent_graph,
)
from app.memory import session_manager


USER_ID = "section15-advanced-graph-test-user"


async def main() -> None:

    print()
    print("=" * 70)
    print("SECTION 15 - ADVANCED LANGGRAPH TEST")
    print("=" * 70)

    # ========================================================
    # Clean previous session
    # ========================================================

    await session_manager.delete_session(
        USER_ID,
    )

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
            jd_id="google-backend",
            title="Backend Engineer",
            company="Google",
            description=(
                "Python, FastAPI, PostgreSQL, "
                "AWS and Docker."
            ),
        )

        # ====================================================
        # 3. Add Amazon JD
        # ====================================================

        print("Adding Amazon JD...")

        await session_manager.add_jd(
            user_id=USER_ID,
            jd_id="amazon-backend",
            title="Software Development Engineer",
            company="Amazon",
            description=(
                "Python, distributed systems, "
                "AWS and Docker."
            ),
        )

        # Newly added JD is active.
        session = await session_manager.get_session(
            USER_ID,
        )

        print()
        print(
            "Initial active JD:",
            session.active_jd_id,
        )

        assert session.active_jd_id == (
            "amazon-backend"
        )

        # ====================================================
        # 4. Test direct graph invocation
        # ====================================================

        print()
        print("Executing LangGraph directly...")

        graph_result = await agent_graph.ainvoke(
            {
                "user_id": USER_ID,
                "message": (
                    "What skills from my resume "
                    "are relevant to this role?"
                ),
                "jd_id": "amazon-backend",
            }
        )

        print()
        print("GRAPH RESULT")
        print("-" * 70)

        print(
            "Answer:",
            graph_result.get(
                "answer",
                "",
            ),
        )

        print(
            "Active JD:",
            (
                graph_result["active_jd"].jd_id
                if graph_result.get(
                    "active_jd"
                )
                else None
            ),
        )

        print(
            "Retrieved chunks:",
            len(
                graph_result.get(
                    "retrieved_chunks",
                    [],
                )
            ),
        )

        # ====================================================
        # 5. Verify graph state
        # ====================================================

        assert graph_result.get(
            "answer"
        )

        assert (
            graph_result[
                "active_jd"
            ].jd_id
            == "amazon-backend"
        )

        assert (
            "amazon-backend"
            in graph_result[
                "metadata"
            ]["available_jd_ids"]
        )

        assert (
            "google-backend"
            in graph_result[
                "metadata"
            ]["available_jd_ids"]
        )

        # ====================================================
        # 6. Test AgentService -> LangGraph
        # ====================================================

        print()
        print("Executing through AgentService...")

        response = await agent_service.chat(
            AgentRequest(
                user_id=USER_ID,
                message=(
                    "Now switch to Google and "
                    "tell me what skills I should "
                    "highlight."
                ),
            )
        )

        print()
        print("SERVICE RESULT")
        print("-" * 70)

        print(
            "Response:",
            response.message,
        )

        print(
            "Active JD:",
            response.jd_id,
        )

        print(
            "Retrieved chunks:",
            response.retrieved_chunks,
        )

        # ====================================================
        # 7. Verify JD switching happened inside graph
        # ====================================================

        assert response.jd_id == (
            "google-backend"
        )

        session = await session_manager.get_session(
            USER_ID,
        )

        assert session.active_jd_id == (
            "google-backend"
        )

        # ====================================================
        # 8. Verify conversation persistence
        # ====================================================

        print()
        print(
            "Stored messages:",
            len(session.messages),
        )

        assert len(session.messages) == 4

        # Direct graph request:
        #   user + assistant = 2
        #
        # AgentService request:
        #   user + assistant = 2
        #
        # Total = 4

        # ====================================================
        # 9. Verify both JDs remain in same session
        # ====================================================

        assert set(
            session.jd_contexts.keys()
        ) == {
            "google-backend",
            "amazon-backend",
        }

        # ====================================================
        # 10. Final state
        # ====================================================

        print()
        print("=" * 70)
        print("FINAL GRAPH STATE")
        print("=" * 70)

        print(
            "Available JDs:",
            list(
                session.jd_contexts.keys()
            ),
        )

        print(
            "Active JD:",
            session.active_jd_id,
        )

        print(
            "Messages:",
            len(session.messages),
        )

        print()
        print("=" * 70)
        print("SECTION 15 PASSED")
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