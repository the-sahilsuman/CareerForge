from uuid import UUID

from app.repositories.agentic_email import (
    AgenticEmailRepository,
)


class AgenticEmailService:

    def __init__(
        self,
        repository: AgenticEmailRepository,
    ):
        self.repository = repository

    async def list_emails(
        self,
        user_id: UUID,
    ) -> list[dict]:

        return await self.repository.get_by_user_id(
            user_id
        )