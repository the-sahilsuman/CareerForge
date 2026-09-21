from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application


class ApplicationRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(
        self,
        user_id: UUID,
    ) -> list[Application]:

        result = await self.db.execute(
            select(Application)
            .where(Application.user_id == user_id)
            .order_by(Application.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        application_id: UUID,
        user_id: UUID,
    ) -> Application | None:

        result = await self.db.execute(
            select(Application).where(
                Application.id == application_id,
                Application.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        application: Application,
    ) -> Application:

        self.db.add(application)

        await self.db.flush()

        return application

    async def delete(
        self,
        application: Application,
    ) -> None:

        await self.db.delete(application)

        await self.db.flush()
