from uuid import UUID

from google.oauth2.credentials import Credentials

from app.core.config import settings
from app.core.encryption import decrypt_token
from app.core.errors import ResourceNotFoundError, ValidationError
from app.models.email_connection import EmailConnection
from app.repositories.email_connection import EmailConnectionRepository


class GmailCredentialService:

    def __init__(
        self,
        repository: EmailConnectionRepository,
    ):
        self.repository = repository

    async def get_credentials(
        self,
        user_id: UUID,
        connection_id: UUID,
    ) -> Credentials:

        connection = await self.repository.get_by_id(
            connection_id
        )

        if connection is None:
            raise ResourceNotFoundError(
                "Email connection not found."
            )

        if connection.user_id != user_id:
            raise ResourceNotFoundError(
                "Email connection not found."
            )

        if connection.access_token_encrypted is None:
            raise ValidationError(
                "Email connection does not have an access token."
            )

        access_token = decrypt_token(
            connection.access_token_encrypted
        )

        refresh_token = None

        if connection.refresh_token_encrypted:
            refresh_token = decrypt_token(
                connection.refresh_token_encrypted
            )

        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            scopes=[
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/userinfo.email",
            ],
        )

        return credentials