from uuid import UUID

from app.core.errors import ResourceNotFoundError
from app.models.email import Email
from app.repositories.email import EmailRepository


class EmailService:

    def __init__(
        self,
        repository: EmailRepository,
    ):
        self.repository = repository

    async def list_emails(
        self,
        user_id: UUID,
    ) -> list[Email]:

        return await self.repository.get_by_user_id(
            user_id
        )

    async def get_email(
        self,
        user_id: UUID,
        email_id: UUID,
    ) -> Email:

        email = await self.repository.get_by_id(
            email_id
        )

        if email is None or email.user_id != user_id:
            raise ResourceNotFoundError(
                "Email not found."
            )

        return email

    async def list_application_emails(
        self,
        user_id: UUID,
        application_id: UUID,
    ) -> list[Email]:

        return await self.repository.get_by_application_id(
            user_id,
            application_id,
        )