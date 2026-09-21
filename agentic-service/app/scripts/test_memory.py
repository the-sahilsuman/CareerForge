import asyncio

from app.memory import session_manager


USER_ID = "section6-test-user"


async def main() -> None:

    print("\nCreating session...")

    session = await session_manager.get_or_create(
        USER_ID,
    )

    print(
        "User:",
        session.user_id,
    )

    print(
        "Initial messages:",
        len(session.messages),
    )

    # --------------------------------------------------------
    # Add first JD
    # --------------------------------------------------------

    await session_manager.add_jd(
        user_id=USER_ID,
        jd_id="jd-001",
        title="Backend Engineer",
        company="Company A",
        description=(
            "Python FastAPI AWS PostgreSQL "
            "Docker Kubernetes"
        ),
    )

    # --------------------------------------------------------
    # Add second JD
    # --------------------------------------------------------

    await session_manager.add_jd(
        user_id=USER_ID,
        jd_id="jd-002",
        title="Cloud Engineer",
        company="Company B",
        description=(
            "AWS Terraform Kubernetes "
            "Linux Docker"
        ),
    )

    # --------------------------------------------------------
    # Add conversation
    # --------------------------------------------------------

    await session_manager.add_message(
        user_id=USER_ID,
        role="user",
        content=(
            "Compare my profile with these jobs."
        ),
    )

    await session_manager.add_message(
        user_id=USER_ID,
        role="assistant",
        content=(
            "I will compare your profile "
            "with the active job."
        ),
    )

    # --------------------------------------------------------
    # Read session
    # --------------------------------------------------------

    session = await session_manager.get_session(
        USER_ID,
    )

    print("\n========== SESSION ==========")

    print(
        "User:",
        session.user_id,
    )

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

    # --------------------------------------------------------
    # Switch JD
    # --------------------------------------------------------

    await session_manager.set_active_jd(
        user_id=USER_ID,
        jd_id="jd-001",
    )

    active_jd = (
        await session_manager.get_active_jd(
            USER_ID,
        )
    )

    print("\n========== ACTIVE JD ==========")

    print(
        "JD:",
        active_jd.jd_id if active_jd else None,
    )

    print(
        "Title:",
        active_jd.title if active_jd else None,
    )

    print(
        "Company:",
        active_jd.company if active_jd else None,
    )

    # --------------------------------------------------------
    # TTL
    # --------------------------------------------------------

    ttl = await session_manager.get_ttl(
        USER_ID,
    )

    print("\n========== REDIS ==========")

    print(
        "TTL:",
        ttl,
        "seconds",
    )

    print(
        "============================\n"
    )

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    await session_manager.delete_session(
        USER_ID,
    )

    print(
        "Test session deleted."
    )


if __name__ == "__main__":
    asyncio.run(main())