from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_connection import EmailConnection
from app.models.enums import EmailProvider


class EmailConnectionRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_by_id(
        self,
        connection_id: UUID,
    ) -> EmailConnection | None:

        result = await self.db.execute(
            select(EmailConnection).where(
                EmailConnection.id == connection_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> EmailConnection | None:

        result = await self.db.execute(
            select(EmailConnection)
            .where(
                EmailConnection.user_id == user_id
            )
            .order_by(
                EmailConnection.created_at.desc()
            )
        )

        return result.scalars().first()

    async def get_by_user_and_provider(
        self,
        user_id: UUID,
        provider: EmailProvider,
    ) -> EmailConnection | None:

        result = await self.db.execute(
            select(EmailConnection).where(
                EmailConnection.user_id == user_id,
                EmailConnection.provider == provider,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        connection: EmailConnection,
    ) -> EmailConnection:

        self.db.add(connection)

        await self.db.flush()

        return connection

    async def update(
        self,
        connection: EmailConnection,
    ) -> EmailConnection:

        await self.db.flush()

        return connection

    async def delete(
        self,
        connection: EmailConnection,
    ) -> None:

        await self.db.delete(connection)

        await self.db.flush()