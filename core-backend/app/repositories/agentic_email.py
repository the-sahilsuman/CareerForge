from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AgenticEmailRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> list[dict]:

        result = await self.db.execute(
            text(
                """
                SELECT
                    id,
                    user_id,
                    role,
                    hr_email,
                    company_name,
                    sent_at
                FROM agentic.emails
                WHERE user_id = :user_id
                ORDER BY sent_at DESC
                """
            ),
            {
                "user_id": str(user_id),
            },
        )

        return [
            dict(row)
            for row in result.mappings().all()
        ]