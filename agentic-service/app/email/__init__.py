from app.email.connection import (
    EmailConnectionError,
    EmailConnectionService,
    EmailCredentials,
    EmailCredentialsError,
    EmailNotConnectedError,
    EmailConnectionStatusResult,
    email_connection_service,
)

from app.email.drafting import (
    EMAIL_DRAFT_SYSTEM_PROMPT,
    EmailDraft,
    EmailDraftingService,
    build_email_draft_prompt,
)

from app.email.execution import (
    EmailExecutionError,
    EmailSendResult,
    GmailEmailExecutor,
    GmailSendError,
    ResumeDownloadError,
    ResumeFormatError,
    ResumeNotFoundError,
)


__all__ = [
    "EmailConnectionError",
    "EmailConnectionService",
    "EmailCredentials",
    "EmailCredentialsError",
    "EmailNotConnectedError",
    "EmailConnectionStatusResult",
    "email_connection_service",

    "EMAIL_DRAFT_SYSTEM_PROMPT",
    "EmailDraft",
    "EmailDraftingService",
    "build_email_draft_prompt",

    "EmailExecutionError",
    "EmailSendResult",
    "GmailEmailExecutor",
    "GmailSendError",
    "ResumeDownloadError",
    "ResumeFormatError",
    "ResumeNotFoundError",
]