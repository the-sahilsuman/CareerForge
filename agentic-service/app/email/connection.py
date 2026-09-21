from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

import httpx

from sqlalchemy import (
    Column,
    DateTime,
    MetaData,
    String,
    Table,
    select,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal


logger = get_logger(__name__)


# ============================================================
# Email Connections Table
# ============================================================
#
# Read-only representation of the table owned by Core Backend.
#
# Agentic Service does NOT own or migrate this table.
#
# ============================================================

metadata = MetaData()

email_connections = Table(
    "email_connections",
    metadata,

    Column(
        "id",
        PGUUID(as_uuid=True),
        primary_key=True,
    ),

    Column(
        "user_id",
        PGUUID(as_uuid=True),
        nullable=False,
    ),

    Column(
        "provider",
        String,
        nullable=False,
    ),

    Column(
        "email_address",
        String,
        nullable=False,
    ),

    Column(
        "status",
        String,
        nullable=False,
    ),

    Column(
        "access_token_encrypted",
        String,
        nullable=True,
    ),

    Column(
        "refresh_token_encrypted",
        String,
        nullable=True,
    ),

    Column(
        "expires_at",
        DateTime(timezone=True),
        nullable=True,
    ),
)


# ============================================================
# Exceptions
# ============================================================


class EmailConnectionError(Exception):
    """Base exception for email connection errors."""


class EmailNotConnectedError(
    EmailConnectionError,
):
    """Raised when no active email connection exists."""


class EmailCredentialsError(
    EmailConnectionError,
):
    """Raised when OAuth credentials cannot be loaded."""


# ============================================================
# Runtime Credentials
# ============================================================


@dataclass(slots=True)
class EmailCredentials:

    provider: str

    email_address: str

    access_token: str

    refresh_token: str | None

    expires_at: datetime | None

    connection_id: UUID


# ============================================================
# Connection Status
# ============================================================


@dataclass(slots=True)
class EmailConnectionStatusResult:

    connected: bool

    provider: str | None = None

    email_address: str | None = None

    expires_at: datetime | None = None

    connection_id: UUID | None = None


# ============================================================
# Service
# ============================================================


class EmailConnectionService:

    """
    Reads email connection information.

    OAuth ownership belongs to Core Backend.

    Agentic Service:
        - reads access token
        - checks expires_at
        - requests refresh from Core Backend
        - uses returned access token

    Agentic Service NEVER handles the Google refresh token.
    """

    CORE_REFRESH_PATH = (
        "/api/v1/email-connections/internal"
    )

    # --------------------------------------------------------
    # Get DB Row
    # --------------------------------------------------------

    async def get_connection_row(
        self,
        user_id: str,
    ):
        """
        Get the email connection belonging to a user.
        """

        try:

            parsed_user_id = UUID(
                user_id,
            )

        except ValueError as exc:

            raise EmailConnectionError(
                f"Invalid user ID: {user_id}",
            ) from exc

        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(
                    email_connections,
                ).where(
                    email_connections.c.user_id
                    == parsed_user_id,
                )
            )

            return result.mappings().first()

    # --------------------------------------------------------
    # Check Connection
    # --------------------------------------------------------

    async def check_connection(
        self,
        user_id: str,
    ) -> EmailConnectionStatusResult:

        row = await self.get_connection_row(
            user_id,
        )

        if row is None:

            logger.info(
                "No email connection found: user=%s",
                user_id,
            )

            return EmailConnectionStatusResult(
                connected=False,
            )

        status = str(
            row["status"],
        )

        connected = (
            status.upper()
            == "ACTIVE"
        )

        return EmailConnectionStatusResult(
            connected=connected,
            provider=(
                str(
                    row["provider"],
                )
                if row["provider"]
                else None
            ),
            email_address=(
                row["email_address"]
            ),
            expires_at=(
                row["expires_at"]
            ),
            connection_id=(
                row["id"]
            ),
        )

    # --------------------------------------------------------
    # Get Credentials
    # --------------------------------------------------------

    async def get_credentials(
        self,
        user_id: str,
    ) -> EmailCredentials:

        row = await self.get_connection_row(
            user_id,
        )

        if row is None:

            raise EmailNotConnectedError(
                "No email account is connected.",
            )

        status = str(
            row["status"],
        )

        if status.upper() != "ACTIVE":

            raise EmailNotConnectedError(
                "Email account is not connected.",
            )

        encrypted_access_token = row[
            "access_token_encrypted"
        ]

        if not encrypted_access_token:

            raise EmailCredentialsError(
                "Encrypted access token is missing.",
            )

        access_token = (
            self._decrypt_token(
                encrypted_access_token,
            )
        )

        credentials = EmailCredentials(
            provider=str(
                row["provider"],
            ),
            email_address=(
                row["email_address"]
            ),
            access_token=access_token,

            # ------------------------------------------------
            # IMPORTANT:
            #
            # Do NOT decrypt or expose the refresh token.
            #
            # Core Backend owns it.
            # ------------------------------------------------

            refresh_token=None,

            expires_at=(
                row["expires_at"]
            ),

            connection_id=(
                row["id"]
            ),
        )

        logger.info(
            "Email credentials loaded: "
            "user=%s provider=%s connection=%s",
            user_id,
            credentials.provider,
            credentials.connection_id,
        )

        return credentials

    # --------------------------------------------------------
    # Ensure Access Token Is Valid
    # --------------------------------------------------------

    async def ensure_valid_credentials(
        self,
        credentials: EmailCredentials,
    ) -> EmailCredentials:
        """
        Check access-token expiry.

        If expired, ask Core Backend to refresh it.

        The refresh token never enters Agentic Service.
        """

        if credentials.expires_at is None:

            logger.warning(
                "Email access token has no expiry: "
                "connection=%s",
                credentials.connection_id,
            )

            return credentials

        expires_at = credentials.expires_at

        if expires_at.tzinfo is None:

            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        now = datetime.now(
            timezone.utc
        )

        if expires_at > now:

            return credentials

        logger.warning(
            "Google access token expired. "
            "Requesting refresh from Core Backend: "
            "connection=%s expires_at=%s",
            credentials.connection_id,
            expires_at,
        )

        refreshed = (
            await self.refresh_via_core_backend(
                credentials.connection_id,
            )
        )

        return EmailCredentials(
            provider=credentials.provider,
            email_address=credentials.email_address,
            access_token=refreshed["access_token"],
            refresh_token=None,
            expires_at=refreshed["expires_at"],
            connection_id=credentials.connection_id,
        )

    # --------------------------------------------------------
    # Refresh Through Core Backend
    # --------------------------------------------------------

    async def refresh_via_core_backend(
        self,
        connection_id: UUID,
    ) -> dict:
        """
        Ask Core Backend to refresh the Google access token.

        Agentic Service sends only:
            connection_id

        Agentic Service does NOT send:
            refresh_token
            client_id
            client_secret
        """

        base_url = (
            settings.core_backend_url.rstrip("/")
        )

        url = (
            f"{base_url}"
            f"{self.CORE_REFRESH_PATH}"
            f"/{connection_id}/refresh"
        )

        headers = {
            "X-CareerForge-Service-Key": (
                settings.internal_service_key
            ),
        }

        try:

            async with httpx.AsyncClient(
                timeout=30.0,
            ) as client:

                response = await client.post(
                    url,
                    headers=headers,
                )

        except httpx.RequestError as exc:

            logger.error(
                "Core Backend token refresh request failed: "
                "connection=%s error=%s",
                connection_id,
                type(exc).__name__,
            )

            raise EmailCredentialsError(
                "Unable to contact Core Backend "
                "for Google token refresh."
            ) from exc

        if response.status_code >= 400:

            try:
                detail = response.json().get(
                    "detail",
                    "Google token refresh failed.",
                )

            except Exception:

                detail = (
                    "Google token refresh failed."
                )

            logger.error(
                "Core Backend token refresh failed: "
                "connection=%s status=%s",
                connection_id,
                response.status_code,
            )

            raise EmailCredentialsError(
                str(detail)
            )

        try:

            data = response.json()

        except Exception as exc:

            raise EmailCredentialsError(
                "Core Backend returned an invalid "
                "token refresh response."
            ) from exc

        access_token = data.get(
            "access_token"
        )

        expires_at_raw = data.get(
            "expires_at"
        )

        if not access_token:

            raise EmailCredentialsError(
                "Core Backend did not return a new "
                "Google access token."
            )

        if not expires_at_raw:

            raise EmailCredentialsError(
                "Core Backend did not return token expiry."
            )

        try:

            expires_at = datetime.fromisoformat(
                expires_at_raw.replace(
                    "Z",
                    "+00:00",
                )
            )

        except (TypeError, ValueError) as exc:

            raise EmailCredentialsError(
                "Core Backend returned an invalid "
                "token expiry."
            ) from exc

        logger.info(
            "Google access token refreshed through "
            "Core Backend: connection=%s expires_at=%s",
            connection_id,
            expires_at,
        )

        return {
            "access_token": access_token,
            "expires_at": expires_at,
        }

    # --------------------------------------------------------
    # Decrypt Access Token
    # --------------------------------------------------------

    @staticmethod
    def _decrypt_token(
        encrypted_token: str,
    ) -> str:

        encryption_key = getattr(
            settings,
            "email_token_encryption_key",
            None,
        )

        if not encryption_key:

            raise EmailCredentialsError(
                "EMAIL_TOKEN_ENCRYPTION_KEY is not configured.",
            )

        try:

            from cryptography.fernet import (
                Fernet,
                InvalidToken,
            )

            fernet = Fernet(
                encryption_key.encode(
                    "utf-8",
                ),
            )

            decrypted = fernet.decrypt(
                encrypted_token.encode(
                    "utf-8",
                ),
            )

            return decrypted.decode(
                "utf-8",
            )

        except InvalidToken as exc:

            raise EmailCredentialsError(
                "Unable to decrypt email OAuth token. "
                "Check that the same encryption key used "
                "by Core Backend is configured.",
            ) from exc

        except Exception as exc:

            raise EmailCredentialsError(
                "Failed to decrypt email OAuth token.",
            ) from exc


# ============================================================
# Singleton
# ============================================================

email_connection_service = (
    EmailConnectionService()
)


__all__ = [
    "EmailConnectionError",
    "EmailConnectionService",
    "EmailCredentials",
    "EmailCredentialsError",
    "EmailNotConnectedError",
    "EmailConnectionStatusResult",
    "email_connection_service",
]