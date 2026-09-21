from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.outbox import OutboxRepository


class OutboxService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = OutboxRepository(session)

    async def enqueue(
        self,
        *,
        event_type: str,
        aggregate_type: str,
        aggregate_id: UUID,
        payload: dict,
    ) -> None:
        await self.repository.create(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload,
        )