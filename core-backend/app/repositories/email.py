from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email import Email


class EmailRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        email_id: UUID,
    ) -> Email | None:

        result = await self.db.execute(
            select(Email).where(
                Email.id == email_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> list[Email]:

        result = await self.db.execute(
            select(Email)
            .where(
                Email.user_id == user_id
            )
            .order_by(
                Email.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def get_by_application_id(
        self,
        user_id: UUID,
        application_id: UUID,
    ) -> list[Email]:

        result = await self.db.execute(
            select(Email)
            .where(
                Email.user_id == user_id,
                Email.application_id == application_id,
            )
            .order_by(
                Email.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def create(
        self,
        email: Email,
    ) -> Email:

        self.db.add(email)

        await self.db.flush()

        return email

    async def update(
        self,
        email: Email,
    ) -> Email:

        await self.db.flush()

        return email