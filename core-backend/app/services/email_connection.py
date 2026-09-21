from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from uuid import UUID
import httpx
import logging

from google.oauth2.credentials import Credentials
from jose import JWTError, jwt

from app.clients.email.gmail import get_google_account_email
from app.clients.google_oauth import create_google_flow
from app.core.config import settings
from app.core.encryption import (
    decrypt_token,
    encrypt_token,
)
from app.core.errors import (
    ConflictError,
    ResourceNotFoundError,
    ValidationError,
)
from app.models.email_connection import EmailConnection
from app.models.enums import EmailProvider
from app.repositories.email_connection import (
    EmailConnectionRepository,
)
from app.repositories.profile import ProfileRepository

logger = logging.getLogger(__name__)


OAUTH_STATE_ALGORITHM = "HS256"
OAUTH_STATE_EXPIRE_MINUTES = 10
OAUTH_STATE_PURPOSE = "google_email_connection"


class EmailConnectionService:

    def __init__(
        self,
        repository: EmailConnectionRepository,
        profile_repository: ProfileRepository,
    ):
        self.repository = repository
        self.profile_repository = profile_repository

    # ============================================================
    # GET CONNECTIONS
    # ============================================================

    async def get_connections(
        self,
        user_id: UUID,
    ) -> list[EmailConnection]:

        connection = await self.repository.get_by_user_id(
            user_id
        )

        if connection is None:
            return []

        return [connection]

    # ============================================================
    # START GOOGLE OAUTH
    # ============================================================

    def get_google_authorization_url(
        self,
        user_id: UUID,
    ) -> str:

        # --------------------------------------------------------
        # Generate our own PKCE verifier.
        #
        # This verifier MUST be available again during callback.
        # --------------------------------------------------------

        code_verifier = token_urlsafe(64)

        flow = create_google_flow(
            code_verifier=code_verifier
        )

        # --------------------------------------------------------
        # Store everything required to safely complete OAuth.
        #
        # The state is signed, so the callback cannot modify it
        # without invalidating the signature.
        # --------------------------------------------------------

        now = datetime.now(timezone.utc)

        state = jwt.encode(
            {
                "user_id": str(user_id),
                "purpose": OAUTH_STATE_PURPOSE,
                "code_verifier": code_verifier,
                "iat": int(now.timestamp()),
                "exp": int(
                    (
                        now
                        + timedelta(
                            minutes=OAUTH_STATE_EXPIRE_MINUTES
                        )
                    ).timestamp()
                ),
            },
            settings.google_oauth_state_secret,
            algorithm=OAUTH_STATE_ALGORITHM,
        )

        authorization_url, _ = (
            flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="consent",
                state=state,
            )
        )

        return authorization_url

    # ============================================================
    # DECODE GOOGLE OAUTH STATE
    # ============================================================

    def decode_google_oauth_state(
        self,
        state: str,
    ) -> tuple[UUID, str]:

        try:
            payload = jwt.decode(
                state,
                settings.google_oauth_state_secret,
                algorithms=[
                    OAUTH_STATE_ALGORITHM
                ],
            )

        except JWTError as exc:
            raise ValidationError(
                "Invalid or expired Google OAuth state."
            ) from exc

        # --------------------------------------------------------
        # Verify purpose
        # --------------------------------------------------------

        if payload.get("purpose") != OAUTH_STATE_PURPOSE:
            raise ValidationError(
                "Invalid Google OAuth state."
            )

        # --------------------------------------------------------
        # Extract user ID
        # --------------------------------------------------------

        user_id = payload.get("user_id")

        if not user_id:
            raise ValidationError(
                "Invalid Google OAuth user."
            )

        try:
            parsed_user_id = UUID(user_id)

        except ValueError as exc:
            raise ValidationError(
                "Invalid Google OAuth user."
            ) from exc

        # --------------------------------------------------------
        # Extract PKCE verifier
        # --------------------------------------------------------

        code_verifier = payload.get(
            "code_verifier"
        )

        if not code_verifier:
            raise ValidationError(
                "Missing Google OAuth code verifier."
            )

        return (
            parsed_user_id,
            code_verifier,
        )

    # ============================================================
    # CONNECT GOOGLE
    # ============================================================

    async def connect_google(
        self,
        user_id: UUID,
        code: str,
        code_verifier: str,
    ) -> EmailConnection:

        # --------------------------------------------------------
        # Get user's profile
        # --------------------------------------------------------

        profile = (
            await self.profile_repository.get_by_user_id(
                user_id
            )
        )

        if profile is None:
            raise ResourceNotFoundError(
                "Profile not found."
            )

        # --------------------------------------------------------
        # Professional email is required
        # --------------------------------------------------------

        if not profile.professional_email:
            raise ValidationError(
                "Set your professional email before connecting Gmail."
            )

        # --------------------------------------------------------
        # Create OAuth flow with ORIGINAL PKCE verifier
        # --------------------------------------------------------

        flow = create_google_flow(
            code_verifier=code_verifier
        )

        try:

            flow.fetch_token(
                code=code
            )

        except Exception as exc:

            print(
                "Google token exchange failed:",
                repr(exc),
            )

            raise ValidationError(
                "Unable to complete Google authorization."
            ) from exc

        credentials = flow.credentials

        # --------------------------------------------------------
        # Get Google account email
        # --------------------------------------------------------

        email_address = (
            get_google_account_email(
                credentials
            )
        )

        if not email_address:
            raise ValidationError(
                "Unable to determine Google account email."
            )

        # --------------------------------------------------------
        # Normalize emails
        # --------------------------------------------------------

        profile_email = (
            profile.professional_email
            .strip()
            .lower()
        )

        google_email = (
            email_address
            .strip()
            .lower()
        )

        # --------------------------------------------------------
        # Google account must match professional email
        # --------------------------------------------------------

        if profile_email != google_email:

            raise ValidationError(
                "The Google account must match your professional email."
            )

        # --------------------------------------------------------
        # Check existing connection
        # --------------------------------------------------------

        existing = (
            await self.repository.get_by_user_id(
                user_id
            )
        )

        # --------------------------------------------------------
        # UPDATE EXISTING CONNECTION
        # --------------------------------------------------------

        if existing:

            existing.provider = (
                EmailProvider.GOOGLE
            )

            existing.email_address = (
                email_address
            )

            if credentials.token:
                existing.access_token_encrypted = (
                    encrypt_token(
                        credentials.token
                    )
                )

            if credentials.refresh_token:
                existing.refresh_token_encrypted = (
                    encrypt_token(
                        credentials.refresh_token
                    )
                )

            existing.expires_at = (
                credentials.expiry
            )

            return await self.repository.update(
                existing
            )

        # --------------------------------------------------------
        # CREATE NEW CONNECTION
        # --------------------------------------------------------

        connection = EmailConnection(
            user_id=user_id,
            provider=EmailProvider.GOOGLE,
            email_address=email_address,

            access_token_encrypted=(
                encrypt_token(
                    credentials.token
                )
                if credentials.token
                else None
            ),

            refresh_token_encrypted=(
                encrypt_token(
                    credentials.refresh_token
                )
                if credentials.refresh_token
                else None
            ),

            expires_at=credentials.expiry,
        )

        return await self.repository.create(
            connection
        )


    # ============================================================
    # REFRESH GOOGLE ACCESS TOKEN
    # ============================================================

    async def refresh_google_access_token(
        self,
        connection_id: UUID,
    ) -> dict:
        """
        Refresh an expired Google OAuth access token.

        IMPORTANT:
        Core Backend owns the Google OAuth client credentials
        and refresh token.

        Agentic Service never receives the refresh token.

        Flow:

            Agentic Service
                ↓
            this method
                ↓
            decrypt refresh token
                ↓
            Google OAuth
                ↓
            new access token
                ↓
            update DB
                ↓
            return new access token
        """

        # --------------------------------------------------------
        # 1. Load connection
        # --------------------------------------------------------

        connection = await self.repository.get_by_id(
            connection_id
        )

        if connection is None:
            raise ResourceNotFoundError(
                "Email connection not found."
            )

        # --------------------------------------------------------
        # 2. Verify Google connection
        # --------------------------------------------------------

        if connection.provider != EmailProvider.GOOGLE:
            raise ValidationError(
                "Email connection is not a Google connection."
            )

        # --------------------------------------------------------
        # 3. Verify active connection
        # --------------------------------------------------------

        if str(connection.status).upper() != "ACTIVE":
            raise ValidationError(
                "Email connection is not active."
            )

        # --------------------------------------------------------
        # 4. Refresh token must exist
        # --------------------------------------------------------

        if not connection.refresh_token_encrypted:
            raise ValidationError(
                "Google refresh token is missing. "
                "Reconnect your Gmail account."
            )

        # --------------------------------------------------------
        # 5. Decrypt refresh token
        #
        # The refresh token never leaves Core Backend.
        # --------------------------------------------------------

        refresh_token = decrypt_token(
            connection.refresh_token_encrypted
        )

        # --------------------------------------------------------
        # 6. Ask Google for a new access token
        # --------------------------------------------------------

        payload = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        try:

            async with httpx.AsyncClient(
                timeout=30.0,
            ) as client:

                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data=payload,
                )

        except httpx.RequestError as exc:

            raise ValidationError(
                "Unable to contact Google OAuth service."
            ) from exc

        # --------------------------------------------------------
        # 7. Handle Google failure
        # --------------------------------------------------------

        if response.status_code >= 400:

            try:
                error_data = response.json()

            except Exception:
                error_data = {}

            google_error = error_data.get(
                "error"
            )

            google_description = error_data.get(
                "error_description"
            )

            # ----------------------------------------------------
            # Refresh token revoked/expired.
            # ----------------------------------------------------

            if google_error == "invalid_grant":

                raise ValidationError(
                    "Google authorization has expired or "
                    "been revoked. Please reconnect your Gmail account."
                )

            message = (
                "Google OAuth token refresh failed."
            )

            if google_description:
                message = (
                    f"{message} "
                    f"{google_description}"
                )

            raise ValidationError(
                message
            )

        # --------------------------------------------------------
        # 8. Parse response
        # --------------------------------------------------------

        try:

            token_data = response.json()

        except Exception as exc:

            raise ValidationError(
                "Google returned an invalid OAuth response."
            ) from exc

        new_access_token = token_data.get(
            "access_token"
        )

        if not new_access_token:

            raise ValidationError(
                "Google did not return a new access token."
            )

        # --------------------------------------------------------
        # 9. Calculate expires_at
        #
        # Google gives us expires_in in seconds.
        # We store the absolute expiration timestamp.
        # --------------------------------------------------------

        expires_in = token_data.get(
            "expires_in"
        )

        if expires_in is None:

            raise ValidationError(
                "Google did not return access token expiry information."
            )

        try:

            expires_in = int(
                expires_in
            )

        except (TypeError, ValueError) as exc:

            raise ValidationError(
                "Invalid Google access token expiry."
            ) from exc

        new_expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                seconds=expires_in
            )
        )

        # --------------------------------------------------------
        # 10. Encrypt new access token
        # --------------------------------------------------------

        connection.access_token_encrypted = (
            encrypt_token(
                new_access_token
            )
        )

        connection.expires_at = (
            new_expires_at
        )

        # --------------------------------------------------------
        # 11. Google can rotate the refresh token.
        #
        # If Google returns one, save the new one.
        # Otherwise keep the existing refresh token.
        # --------------------------------------------------------

        new_refresh_token = token_data.get(
            "refresh_token"
        )

        if new_refresh_token:

            connection.refresh_token_encrypted = (
                encrypt_token(
                    new_refresh_token
                )
            )

        # --------------------------------------------------------
        # 12. Persist changes
        #
        # get_db() commits after the request succeeds.
        # --------------------------------------------------------

        await self.repository.update(
            connection
        )

        logger.info(
            "Google access token refreshed: "
            "connection=%s expires_at=%s",
            connection.id,
            new_expires_at,
        )

        # --------------------------------------------------------
        # 13. Return ONLY what Agentic Service needs.
        #
        # NEVER return refresh_token.
        # NEVER return client_secret.
        # --------------------------------------------------------

        return {
            "connection_id": str(
                connection.id
            ),
            "email_address": (
                connection.email_address
            ),
            "access_token": new_access_token,
            "expires_at": new_expires_at,
        }

    # ============================================================
    # DISCONNECT
    # ============================================================

    async def disconnect(
        self,
        user_id: UUID,
        connection_id: UUID,
    ) -> None:

        connection = (
            await self.repository.get_by_id(
                connection_id
            )
        )

        if connection is None:
            raise ResourceNotFoundError(
                "Email connection not found."
            )

        if connection.user_id != user_id:
            raise ResourceNotFoundError(
                "Email connection not found."
            )

        # --------------------------------------------------------
        # Disconnect means COMPLETE deletion of the connection
        # and stored OAuth credentials.
        #
        # Historical emails are NOT deleted because
        # emails.connection_id uses ON DELETE SET NULL.
        # --------------------------------------------------------

        await self.repository.delete(
            connection
        )