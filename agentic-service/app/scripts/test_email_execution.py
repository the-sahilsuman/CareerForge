from __future__ import annotations

import asyncio
import base64
import os
from email import policy
from email.parser import BytesParser

from sqlalchemy import text

from app.db import AsyncSessionLocal
from app.email.connection import EmailCredentials
from app.email.drafting import EmailDraft
from app.email.execution import GmailEmailExecutor


# ============================================================
# SECTION 20 - EMAIL EXECUTION TEST
# ============================================================


async def main() -> None:

    print()
    print("=" * 72)
    print("SECTION 20 - EMAIL EXECUTION")
    print("=" * 72)

    # --------------------------------------------------------
    # User
    # --------------------------------------------------------

    print()

    user_id = input(
        "Enter user_id: "
    ).strip()

    if not user_id:
        raise ValueError(
            "user_id is required."
        )

    # ========================================================
    # 1. FETCH CURRENT RESUME
    # ========================================================

    print()
    print("Fetching current resume...")

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            text(
                """
                SELECT object_url
                FROM public.resumes
                WHERE user_id = :user_id
                LIMIT 1
                """
            ),
            {
                "user_id": user_id,
            },
        )

        resume_row = (
            result.mappings().first()
        )

    if resume_row is None:

        raise RuntimeError(
            f"No resume found in public.resumes "
            f"for user_id={user_id}"
        )

    resume_object_url = resume_row.get(
        "object_url"
    )

    if not resume_object_url:

        raise RuntimeError(
            "Resume exists but object_url is empty."
        )

    print(
        "Resume object URL found."
    )

    # Don't print the complete URL because it may
    # contain a signed URL/token.

    print(
        "Resume URL retrieved successfully."
    )

    # ========================================================
    # 2. TEST CREDENTIALS
    # ========================================================
    #
    # This test DOES NOT send anything to Gmail.
    #
    # Therefore this is a fake access token.
    #
    # ========================================================

    credentials = EmailCredentials(
        provider="gmail",
        email_address="test@example.com",
        access_token="TEST_TOKEN",
        refresh_token=None,
        expires_at=None,
        connection_id=None,
    )

    # ========================================================
    # 3. SAMPLE EMAIL DRAFT
    # ========================================================

    draft = EmailDraft(
        recipient_email="recruiter@example.com",
        recipient_name="Hiring Team",
        subject="Application for Backend Engineer",
        body=(
            "Dear Hiring Team,\n\n"
            "I am writing to express my interest in "
            "the Backend Engineer position. My experience "
            "with Python, FastAPI, PostgreSQL, AWS and "
            "Docker aligns with the requirements of the role.\n\n"
            "I would be glad to discuss my profile further.\n\n"
            "Regards,\n"
            "Sahil Suman"
        ),
        sender_name="Sahil Suman",
        sender_email="test@example.com",
        sender_mobile=None,
        attachment_required=True,
        attachment_type="resume",
    )

    # ========================================================
    # 4. CREATE EXECUTOR
    # ========================================================

    executor = GmailEmailExecutor()

    resume_path: str | None = None
    pdf_path: str | None = None

    try:

        # ====================================================
        # 5. DOWNLOAD RESUME
        # ====================================================

        print()
        print("Downloading resume...")

        resume_path = (
            await executor._download_resume(
                resume_object_url
            )
        )

        if not os.path.exists(
            resume_path
        ):

            raise RuntimeError(
                "Downloaded resume file does not exist."
            )

        file_size = os.path.getsize(
            resume_path
        )

        if file_size == 0:

            raise RuntimeError(
                "Downloaded resume is empty."
            )

        print(
            "Resume downloaded successfully."
        )

        print(
            f"Temporary file: {resume_path}"
        )

        print(
            f"File size: {file_size} bytes"
        )

        # ====================================================
        # 6. ENSURE PDF
        # ====================================================

        print()
        print("Preparing resume as PDF...")

        pdf_path = (
            await executor._ensure_pdf(
                resume_path
            )
        )

        if not os.path.exists(
            pdf_path
        ):

            raise RuntimeError(
                "PDF file was not created."
            )

        pdf_size = os.path.getsize(
            pdf_path
        )

        if pdf_size == 0:

            raise RuntimeError(
                "PDF file is empty."
            )

        print(
            "PDF prepared successfully."
        )

        print(
            f"PDF file: {pdf_path}"
        )

        print(
            f"PDF size: {pdf_size} bytes"
        )

        # ====================================================
        # 7. VERIFY PDF FORMAT
        # ====================================================

        with open(
            pdf_path,
            "rb",
        ) as file:

            pdf_header = file.read(
                4
            )

        if pdf_header != b"%PDF":

            raise RuntimeError(
                "Prepared resume is not a valid PDF."
            )

        print(
            "PDF format verified."
        )

        # ====================================================
        # 8. BUILD MIME EMAIL
        # ====================================================

        print()
        print("Building MIME email...")

        raw_message = (
            await executor._build_mime_message(
                draft=draft,
                credentials=credentials,
                pdf_path=pdf_path,
            )
        )

        if not raw_message:

            raise RuntimeError(
                "MIME message is empty."
            )

        print(
            "MIME message created successfully."
        )

        # ====================================================
        # 9. DECODE MIME MESSAGE
        # ====================================================

        print()
        print("Validating MIME message...")

        raw_bytes = (
            base64.urlsafe_b64decode(
                raw_message
            )
        )

        message = (
            BytesParser(
                policy=policy.default
            ).parsebytes(
                raw_bytes
            )
        )

        # ====================================================
        # 10. VALIDATE HEADERS
        # ====================================================

        if (
            message["From"]
            != credentials.email_address
        ):

            raise RuntimeError(
                "Incorrect From header."
            )

        if (
            message["To"]
            != draft.recipient_email
        ):

            raise RuntimeError(
                "Incorrect To header."
            )

        if (
            message["Subject"]
            != draft.subject
        ):

            raise RuntimeError(
                "Incorrect Subject header."
            )

        print(
            "Email headers validated."
        )

        # ====================================================
        # 11. VALIDATE BODY
        # ====================================================

        body = message.get_body(
            preferencelist=("plain",)
        )

        if body is None:

            raise RuntimeError(
                "Email body is missing."
            )

        body_content = body.get_content()

        if draft.body.strip() not in body_content:

            raise RuntimeError(
                "Email body does not match the draft."
            )

        print(
            "Email body validated."
        )

        # ====================================================
        # 12. VALIDATE ATTACHMENT
        # ====================================================

        attachments = list(
            message.iter_attachments()
        )

        if not attachments:

            raise RuntimeError(
                "No attachment found."
            )

        if len(attachments) != 1:

            raise RuntimeError(
                f"Expected exactly one attachment, "
                f"found {len(attachments)}."
            )

        attachment = attachments[0]

        content_type = (
            attachment.get_content_type()
        )

        filename = (
            attachment.get_filename()
        )

        payload = (
            attachment.get_payload(
                decode=True
            )
        )

        if content_type != "application/pdf":

            raise RuntimeError(
                f"Expected application/pdf, "
                f"got {content_type}"
            )

        if filename != "resume.pdf":

            raise RuntimeError(
                f"Expected resume.pdf, "
                f"got {filename}"
            )

        if not payload:

            raise RuntimeError(
                "Resume attachment is empty."
            )

        if not payload.startswith(
            b"%PDF"
        ):

            raise RuntimeError(
                "Attachment does not contain a valid PDF."
            )

        print(
            "PDF attachment validated."
        )

        print(
            f"Attachment name: {filename}"
        )

        print(
            f"Attachment type: {content_type}"
        )

        print(
            f"Attachment size: {len(payload)} bytes"
        )

        # ====================================================
        # 13. REAL GMAIL SEND IS SKIPPED
        # ====================================================

        print()
        print(
            "Gmail API call skipped intentionally."
        )

        print(
            "No real email was sent."
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        print()
        print("=" * 72)
        print("SECTION 20 TEST PASSED")
        print("=" * 72)
        print()

    finally:

        # ====================================================
        # CLEANUP
        # ====================================================

        if resume_path:

            executor._cleanup_file(
                resume_path
            )

        if pdf_path:

            executor._cleanup_file(
                pdf_path
            )

        print(
            "Temporary resume files cleaned up."
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )