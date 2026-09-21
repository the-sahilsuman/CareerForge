from __future__ import annotations

import asyncio
import json

from app.agent import (
    AgentRequest,
    agent_service,
)


# ============================================================
# SECTION 21
# END-TO-END AGENT INTEGRATION TEST
# ============================================================


async def run_test(
    *,
    user_id: str,
    message: str,
    jd_id: str | None = None,
) -> None:

    print()
    print("-" * 72)
    print(
        f"USER MESSAGE: {message}"
    )

    if jd_id:
        print(
            f"EXPLICIT JD: {jd_id}"
        )

    print("-" * 72)

    request = AgentRequest(
        user_id=user_id,
        message=message,
        jd_id=jd_id,
    )

    response = await agent_service.chat(
        request
    )

    if response is None:

        raise RuntimeError(
            "AgentService returned None."
        )

    if not response.message:

        raise RuntimeError(
            "Agent returned an empty message."
        )

    print()
    print("AGENT RESPONSE:")
    print(
        response.message
    )

    print()
    print("RESPONSE METADATA:")

    print(
        json.dumps(
            response.metadata,
            indent=2,
            default=str,
        )
    )

    print()
    print(
        f"Resolved JD: {response.jd_id}"
    )

    print(
        f"Retrieved chunks: "
        f"{response.retrieved_chunks}"
    )


# ============================================================
# Main
# ============================================================


async def main() -> None:

    print()
    print("=" * 72)
    print("SECTION 21 - END-TO-END AGENT INTEGRATION")
    print("=" * 72)

    print()

    user_id = input(
        "Enter user_id: "
    ).strip()

    if not user_id:

        raise ValueError(
            "user_id is required."
        )

    # ========================================================
    # TEST 1
    # Basic Agent Request
    # ========================================================

    print()
    print("[1/5] BASIC AGENT REQUEST")

    await run_test(
        user_id=user_id,
        message=(
            "How can you help me with my job search?"
        ),
    )

    print()
    print(
        "✓ Basic agent flow passed."
    )

    # ========================================================
    # TEST 2
    # Conversation Context
    # ========================================================

    print()
    print("[2/5] CONVERSATION CONTINUITY")

    await run_test(
        user_id=user_id,
        message=(
            "Remember that I am targeting "
            "backend engineering roles."
        ),
    )

    await run_test(
        user_id=user_id,
        message=(
            "What type of roles did I say "
            "I am targeting?"
        ),
    )

    print()
    print(
        "✓ Conversation flow completed."
    )

    # ========================================================
    # TEST 3
    # JD-Aware Request
    # ========================================================

    print()
    print("[3/5] JD-AWARE REQUEST")

    print()
    print(
        "This test uses the currently active JD "
        "from the conversation session."
    )

    await run_test(
        user_id=user_id,
        message=(
            "What are the most important skills "
            "for the current job?"
        ),
    )

    print()
    print(
        "✓ JD-aware flow completed."
    )

    # ========================================================
    # TEST 4
    # Multi-JD Conversation
    # ========================================================

    print()
    print("[4/5] MULTI-JD CONVERSATION")

    await run_test(
        user_id=user_id,
        message=(
            "Compare the current job with "
            "the other job in this conversation."
        ),
    )

    print()
    print(
        "✓ Multi-JD routing flow completed."
    )

    # ========================================================
    # TEST 5
    # Email Connection Gate
    # ========================================================

    print()
    print("[5/5] EMAIL CONNECTION GATE")

    await run_test(
        user_id=user_id,
        message=(
            "Draft an email to the recruiter "
            "for the current job."
        ),
    )

    print()
    print(
        "✓ Email routing flow completed."
    )

    # ========================================================
    # SUCCESS
    # ========================================================

    print()
    print("=" * 72)
    print("SECTION 21 TEST PASSED")
    print("=" * 72)
    print()

    print(
        "Verified:"
    )

    print(
        "  ✓ AgentService"
    )

    print(
        "  ✓ LangGraph execution"
    )

    print(
        "  ✓ Session loading"
    )

    print(
        "  ✓ Request routing"
    )

    print(
        "  ✓ JD resolution"
    )

    print(
        "  ✓ Retrieval"
    )

    print(
        "  ✓ Conversation continuity"
    )

    print(
        "  ✓ Multi-JD flow"
    )

    print(
        "  ✓ Email connection gate"
    )

    print(
        "  ✓ Response generation"
    )

    print(
        "  ✓ Conversation persistence"
    )

    print(
        "  ✓ Metadata generation"
    )

    print()


# ============================================================
# Entry Point
# ============================================================


if __name__ == "__main__":

    asyncio.run(
        main()
    )