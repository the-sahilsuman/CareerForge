import asyncio

from app.routing import routing_service


TEST_MESSAGES = [
    "What skills do I have?",
    "What is written in my resume?",
    "Explain this job description.",
    "How well do I match this job?",
    "Switch to the other job.",
    "Draft an email to the recruiter.",
    "How should I prepare for backend interviews?",
]


async def main() -> None:

    print("\n")
    print("=" * 60)
    print("CAREERFORGE INTENT ROUTER TEST")
    print("=" * 60)

    for message in TEST_MESSAGES:

        print("\nUser:")
        print(message)

        result = await routing_service.route(
            message=message,
            active_jd_id="jd-001",
        )

        print("\nResult:")
        print(
            "Intent:",
            result.intent,
        )

        print(
            "JD:",
            result.jd_id,
        )

        print(
            "Confidence:",
            result.confidence,
        )

        print(
            "Reasoning:",
            result.reasoning,
        )

        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())