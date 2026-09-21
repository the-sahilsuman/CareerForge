from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application_event import ApplicationEvent


class ApplicationEventRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_application(
        self,
        application_id: UUID,
    ) -> list[ApplicationEvent]:

        result = await self.db.execute(
            select(ApplicationEvent)
            .where(
                ApplicationEvent.application_id
                == application_id
            )
            .order_by(
                ApplicationEvent.created_at.asc()
            )
        )

        return list(result.scalars().all())

    async def create(
        self,
        event: ApplicationEvent,
    ) -> ApplicationEvent:

        self.db.add(event)

        await self.db.flush()

        return event
