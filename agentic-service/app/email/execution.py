from __future__ import annotations

import asyncio
import base64
import os
import tempfile
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import httpx

from app.core.logging import get_logger
from app.email.connection import (
    EmailCredentials,
    email_connection_service,
)
from app.email.drafting import EmailDraft
from app.storage.s3 import S3ResumeStorage


logger = get_logger(__name__)


# ============================================================
# Exceptions
# ============================================================


class EmailExecutionError(Exception):
    """Base exception for email execution."""


class ResumeNotFoundError(
    EmailExecutionError,
):
    """Raised when the user has no resume."""


class ResumeDownloadError(
    EmailExecutionError,
):
    """Raised when the resume cannot be downloaded."""


class ResumeFormatError(
    EmailExecutionError,
):
    """Raised when the resume cannot be used as PDF."""


class GmailSendError(
    EmailExecutionError,
):
    """Raised when Gmail rejects the message."""


# ============================================================
# Result
# ============================================================


class EmailSendResult:

    def __init__(
        self,
        *,
        provider: str,
        message_id: str,
        thread_id: str | None,
        recipient_email: str,
        subject: str,
        attachment_name: str,
    ) -> None:

        self.provider = provider

        self.message_id = (
            message_id
        )

        self.thread_id = (
            thread_id
        )

        self.recipient_email = (
            recipient_email
        )

        self.subject = subject

        self.attachment_name = (
            attachment_name
        )


# ============================================================
# Executor
# ============================================================


class GmailEmailExecutor:
    """
    Executes an already-created EmailDraft through Gmail.

    Responsibilities:

        EmailDraft
            +
        OAuth credentials
            +
        current resume S3 URL
            ↓
        MIME message
            ↓
        Gmail API
            ↓
        sent message metadata

    This class does NOT:

        - generate email content
        - perform OAuth authorization flow
        - create email DB records

    It DOES:

        - detect a rejected access token
        - request a fresh access token using the
          stored refresh token
        - retry Gmail once
    """

    GMAIL_SEND_URL = (
        "https://gmail.googleapis.com/gmail/v1/"
        "users/me/messages/send"
    )

    def __init__(
        self,
        *,
        s3_storage: S3ResumeStorage | None = None,
    ) -> None:

        self.s3_storage = (
            s3_storage
            or S3ResumeStorage()
        )

    # ========================================================
    # Public API
    # ========================================================

    async def send(
        self,
        *,
        draft: EmailDraft,
        credentials: EmailCredentials,
        resume_s3_url: str,
    ) -> EmailSendResult:

        if not draft.recipient_email:

            raise EmailExecutionError(
                "Cannot send email without a recipient email address."
            )

        if not draft.subject.strip():

            raise EmailExecutionError(
                "Cannot send email without a subject."
            )

        if not draft.body.strip():

            raise EmailExecutionError(
                "Cannot send email with an empty body."
            )

        if not resume_s3_url.strip():

            raise ResumeNotFoundError(
                "No resume S3 URL is available."
            )

        # ----------------------------------------------------
        # CHECK / REFRESH GOOGLE ACCESS TOKEN
        # ----------------------------------------------------

        credentials = (
            await email_connection_service
            .ensure_valid_credentials(
                credentials,
            )
        )

        # ----------------------------------------------------
        # Download current resume
        # ----------------------------------------------------

        resume_path: str | None = None

        try:

            resume_path = (
                await self._download_resume(
                    resume_s3_url,
                )
            )

            pdf_path = (
                await self._ensure_pdf(
                    resume_path,
                )
            )

            raw_message = (
                await self._build_mime_message(
                    draft=draft,
                    credentials=credentials,
                    pdf_path=pdf_path,
                )
            )

            result = await self._send_to_gmail(
                credentials=credentials,
                raw_message=raw_message,
                recipient_email=draft.recipient_email,
                subject=draft.subject,
                attachment_name=self._resume_filename(
                    draft,
                ),
            )

            return result

        finally:

            if resume_path:

                self._cleanup_file(
                    resume_path,
                )

                converted_pdf = (
                    self._converted_pdf_path(
                        resume_path,
                    )
                )

                if converted_pdf != resume_path:

                    self._cleanup_file(
                        converted_pdf,
                    )
                    
    # ========================================================
    # Resume Download
    # ========================================================

    async def _download_resume(
        self,
        s3_url: str,
    ) -> str:

        suffix = (
            self._suffix_from_s3_url(
                s3_url,
            )
        )

        temp = (
            tempfile.NamedTemporaryFile(
                suffix=suffix,
                delete=False,
            )
        )

        temp_path = temp.name

        temp.close()

        try:

            await self.s3_storage.download_resume(
                s3_url=s3_url,
                destination=temp_path,
            )

            if not os.path.exists(
                temp_path,
            ):

                raise ResumeDownloadError(
                    "Resume download did not create a file.",
                )

            if os.path.getsize(
                temp_path,
            ) == 0:

                raise ResumeDownloadError(
                    "Downloaded resume is empty.",
                )

            return temp_path

        except Exception as exc:

            self._cleanup_file(
                temp_path,
            )

            if isinstance(
                exc,
                ResumeDownloadError,
            ):

                raise

            raise ResumeDownloadError(
                "Unable to download resume from S3.",
            ) from exc

    # ========================================================
    # PDF
    # ========================================================

    async def _ensure_pdf(
        self,
        source_path: str,
    ) -> str:

        source = Path(
            source_path,
        )

        # ----------------------------------------------------
        # Already PDF
        # ----------------------------------------------------

        if (
            source.suffix.lower()
            == ".pdf"
        ):

            return source_path

        # ----------------------------------------------------
        # DOCX
        #
        # Production recommendation:
        # LibreOffice should be installed in the runtime
        # image/EC2 environment.
        # ----------------------------------------------------

        if (
            source.suffix.lower()
            == ".docx"
        ):

            return (
                await self._convert_docx_to_pdf(
                    source_path,
                )
            )

        raise ResumeFormatError(
            "The current resume must be PDF or DOCX.",
        )

    # ========================================================
    # DOCX -> PDF
    # ========================================================

    async def _convert_docx_to_pdf(
        self,
        docx_path: str,
    ) -> str:

        output_dir = (
            tempfile.mkdtemp(
                prefix="careerforge_resume_",
            )
        )

        command = [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            output_dir,
            docx_path,
        ]

        try:

            process = (
                await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            )

            stdout, stderr = (
                await process.communicate()
            )

        except FileNotFoundError as exc:

            raise ResumeFormatError(
                "Resume is DOCX but LibreOffice is not "
                "installed. Install LibreOffice in the "
                "agentic-service runtime.",
            ) from exc

        if process.returncode != 0:

            logger.error(
                "DOCX to PDF conversion failed: %s",
                stderr.decode(
                    errors="ignore",
                ),
            )

            raise ResumeFormatError(
                "Unable to convert DOCX resume to PDF.",
            )

        pdf_path = (
            Path(output_dir)
            / f"{Path(docx_path).stem}.pdf"
        )

        if not pdf_path.exists():

            logger.error(
                "LibreOffice output: %s",
                stdout.decode(
                    errors="ignore",
                ),
            )

            raise ResumeFormatError(
                "PDF conversion completed without "
                "producing a PDF file.",
            )

        return str(
            pdf_path,
        )

    # ========================================================
    # MIME Message
    # ========================================================

    async def _build_mime_message(
        self,
        *,
        draft: EmailDraft,
        credentials: EmailCredentials,
        pdf_path: str,
    ) -> str:

        message = EmailMessage()

        message["From"] = (
            credentials.email_address
        )

        message["To"] = (
            draft.recipient_email
        )

        message["Subject"] = (
            draft.subject
        )

        message.set_content(
            draft.body,
        )

        filename = (
            self._resume_filename(
                draft,
            )
        )

        with open(
            pdf_path,
            "rb",
        ) as file:

            pdf_bytes = file.read()

        message.add_attachment(
            pdf_bytes,
            maintype="application",
            subtype="pdf",
            filename=filename,
        )

        raw_bytes = (
            message.as_bytes()
        )

        encoded = (
            base64.urlsafe_b64encode(
                raw_bytes,
            )
            .decode(
                "ascii",
            )
        )

        return encoded

    # ========================================================
    # Gmail API
    # ========================================================

    async def _send_to_gmail(
        self,
        *,
        credentials: EmailCredentials,
        raw_message: str,
        recipient_email: str,
        subject: str,
        attachment_name: str,
    ) -> EmailSendResult:

        # ----------------------------------------------------
        # First attempt
        # ----------------------------------------------------

        headers = {
            "Authorization": (
                "Bearer "
                f"{credentials.access_token}"
            ),
            "Content-Type": (
                "application/json"
            ),
        }

        payload = {
            "raw": raw_message,
        }

        async with httpx.AsyncClient(
            timeout=30.0,
        ) as client:

            response = await client.post(
                self.GMAIL_SEND_URL,
                headers=headers,
                json=payload,
            )

        # ----------------------------------------------------
        # Access token rejected
        #
        # Refresh the token and retry exactly once.
        # ----------------------------------------------------

        if response.status_code == 401:

            logger.warning(
                "Gmail access token rejected. "
                "Attempting OAuth refresh: connection=%s",
                credentials.connection_id,
            )

            try:

                refreshed_credentials = (
                    await email_connection_service
                    .refresh_google_credentials(
                        credentials=credentials,
                    )
                )

            except Exception as exc:

                logger.error(
                    "Google OAuth refresh failed: "
                    "connection=%s error=%s",
                    credentials.connection_id,
                    type(exc).__name__,
                )

                raise GmailSendError(
                    str(exc),
                ) from exc

            # ------------------------------------------------
            # Retry Gmail with fresh access token
            # ------------------------------------------------

            refreshed_headers = {
                "Authorization": (
                    "Bearer "
                    f"{refreshed_credentials.access_token}"
                ),
                "Content-Type": (
                    "application/json"
                ),
            }

            async with httpx.AsyncClient(
                timeout=30.0,
            ) as client:

                response = await client.post(
                    self.GMAIL_SEND_URL,
                    headers=refreshed_headers,
                    json=payload,
                )

        # ----------------------------------------------------
        # Gmail rejected the request
        # ----------------------------------------------------

        if response.status_code >= 400:

            # Never log:
            #
            # - access token
            # - refresh token
            # - complete MIME request
            #
            # Gmail returns useful structured error information for
            # rejected requests. Extract only the safe diagnostic
            # fields instead of logging the complete response body.
            error_message = ""
            error_reason = ""

            try:
                error_data = response.json()
                error = error_data.get("error", {})

                if isinstance(error, dict):
                    error_message = str(
                        error.get("message") or ""
                    )

                    errors = error.get("errors") or []

                    if errors and isinstance(errors[0], dict):
                        error_reason = str(
                            errors[0].get("reason") or ""
                        )

            except Exception:
                # Keep the original HTTP status as the fallback
                # diagnostic if Gmail did not return JSON.
                pass

            logger.error(
                "Gmail send failed: status=%s reason=%s message=%s",
                response.status_code,
                error_reason or "unknown",
                error_message or "unknown",
            )

            # ------------------------------------------------
            # Access token rejected
            # ------------------------------------------------

            if response.status_code == 401:

                raise GmailSendError(
                    "Gmail authorization was rejected. "
                    "Please reconnect your Gmail account.",
                )

            # ------------------------------------------------
            # Gmail permission / policy / quota errors
            # ------------------------------------------------

            raise GmailSendError(
                "Gmail rejected the email request: "
                f"HTTP {response.status_code}"
                + (
                    f" ({error_reason}: {error_message})"
                    if error_reason or error_message
                    else ""
                ),
            )

        # ----------------------------------------------------
        # Parse Gmail response
        # ----------------------------------------------------

        try:

            data: dict[str, Any] = (
                response.json()
            )

        except Exception as exc:

            raise GmailSendError(
                "Gmail returned an invalid response.",
            ) from exc

        # ----------------------------------------------------
        # Message ID
        # ----------------------------------------------------

        message_id = data.get(
            "id",
        )

        if not message_id:

            raise GmailSendError(
                "Gmail accepted the request but did not "
                "return a message ID.",
            )

        # ----------------------------------------------------
        # Successful result
        # ----------------------------------------------------

        return EmailSendResult(
            provider="gmail",
            message_id=message_id,
            thread_id=data.get(
                "threadId",
            ),
            recipient_email=(
                recipient_email
            ),
            subject=subject,
            attachment_name=(
                attachment_name
            ),
        )

    # ========================================================
    # Helpers
    # ========================================================

    @staticmethod
    def _suffix_from_s3_url(
        s3_url: str,
    ) -> str:

        from urllib.parse import urlparse

        parsed = urlparse(
            s3_url,
        )

        filename = (
            Path(
                parsed.path,
            ).name
        )

        suffix = (
            Path(
                filename,
            ).suffix.lower()
        )

        if suffix in {
            ".pdf",
            ".docx",
        }:

            return suffix

        return ".pdf"

    @staticmethod
    def _resume_filename(
        draft: EmailDraft,
    ) -> str:

        return "resume.pdf"

    @staticmethod
    def _converted_pdf_path(
        source_path: str,
    ) -> str:

        source = Path(
            source_path,
        )

        return str(
            source.parent
            / f"{source.stem}.pdf"
        )

    @staticmethod
    def _cleanup_file(
        path: str,
    ) -> None:

        try:

            if os.path.exists(
                path,
            ):

                os.remove(
                    path,
                )

        except OSError:

            logger.warning(
                "Unable to clean temporary file.",
            )


__all__ = [
    "EmailExecutionError",
    "GmailEmailExecutor",
    "GmailSendError",
    "ResumeDownloadError",
    "ResumeFormatError",
    "ResumeNotFoundError",
    "EmailSendResult",
]