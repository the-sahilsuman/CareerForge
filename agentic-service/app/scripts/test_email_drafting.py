from __future__ import annotations

import asyncio

from app.agent.llm import get_llm_provider
from app.email import (
    EmailDraftingService,
)


async def main() -> None:

    print()
    print("=" * 72)
    print("SECTION 19 - EMAIL DRAFTING")
    print("=" * 72)

    llm = get_llm_provider()

    service = EmailDraftingService(
        llm=llm,
    )

    active_jd = """
    Backend Engineer

    We are looking for a backend engineer with experience in
    Python, FastAPI, PostgreSQL, AWS, Docker and REST APIs.

    Responsibilities include building backend services,
    designing APIs, working with databases and deploying
    applications on cloud infrastructure.
    """.strip()

    retrieved_context = """
    Name: Sahil Suman

    Education:
    B.Tech, Electrical Engineering,
    NIT Agartala.

    Skills:
    Python, FastAPI, PostgreSQL, AWS, Docker, Kubernetes,
    Git, Linux, Bash.

    Experience / Projects:
    Built a Doctor Appointment Platform using FastAPI,
    PostgreSQL, Docker and AWS.

    Implemented CI/CD using Jenkins and Docker.

    Worked with AWS EC2, S3, IAM, VPC, ALB,
    CloudWatch and Route53.
    """.strip()

    conversation = """
    User wants to apply for the active Backend Engineer role.
    """.strip()

    print()
    print("Generating email draft...")

    draft = await service.draft(
        user_message=(
            "Draft a concise application email for this role."
        ),
        active_jd=active_jd,
        retrieved_context=retrieved_context,
        conversation=conversation,
    )

    print()
    print("-" * 72)
    print("EMAIL DRAFT")
    print("-" * 72)

    print()
    print("Recipient:")
    print(
        draft.recipient_email
        or "Not provided"
    )

    print()
    print("Subject:")
    print(draft.subject)

    print()
    print("Body:")
    print(draft.body)

    print()
    print("Sender:")
    print(
        draft.sender_name
        or "Not provided"
    )

    print(
        draft.sender_email
        or "Not provided"
    )

    print(
        draft.sender_mobile
        or "Not provided"
    )

    print()
    print(
        "Attachment required:",
        draft.attachment_required,
    )

    print(
        "Attachment type:",
        draft.attachment_type,
    )

    # ========================================================
    # Assertions
    # ========================================================

    assert draft.subject.strip()

    assert draft.body.strip()

    assert (
        draft.attachment_required
        is True
    )

    assert (
        draft.attachment_type
        == "resume"
    )

    # The test data contains these skills,
    # so the draft should have a meaningful
    # role-specific body.

    assert len(
        draft.body.strip()
    ) >= 50

    print()
    print("=" * 72)
    print("SECTION 19 PASSED")
    print("=" * 72)
    print()


if __name__ == "__main__":
    asyncio.run(main())