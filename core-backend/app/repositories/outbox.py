from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox_event import OutboxEvent


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        event_type: str,
        aggregate_type: str,
        aggregate_id: UUID,
        payload: dict,
    ) -> OutboxEvent:
        event = OutboxEvent(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload,
            status="PENDING",
            attempts=0,
            available_at=datetime.now(timezone.utc),
        )

        self.session.add(event)
        await self.session.flush()

        return event

    async def get_pending(
        self,
        *,
        limit: int = 100,
    ) -> list[OutboxEvent]:
        result = await self.session.execute(
            select(OutboxEvent)
            .where(
                OutboxEvent.status == "PENDING",
                OutboxEvent.available_at <= datetime.now(timezone.utc),
            )
            .order_by(OutboxEvent.available_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        return list(result.scalars().all())

    async def mark_processing(
        self,
        event: OutboxEvent,
        worker_id: str,
    ) -> None:
        event.status = "PROCESSING"
        event.locked_at = datetime.now(timezone.utc)
        event.locked_by = worker_id
        event.attempts += 1

        await self.session.flush()

    async def mark_published(
        self,
        event: OutboxEvent,
    ) -> None:
        event.status = "PUBLISHED"
        event.published_at = datetime.now(timezone.utc)
        event.locked_at = None
        event.locked_by = None
        event.last_error = None

        await self.session.flush()

    async def mark_failed(
        self,
        event: OutboxEvent,
        error: str,
        retry_delay_seconds: int,
    ) -> None:
        event.status = "PENDING"
        event.available_at = (
            datetime.now(timezone.utc)
            + timedelta(seconds=retry_delay_seconds)
        )
        event.locked_at = None
        event.locked_by = None
        event.last_error = error[:4000]

        await self.session.flush()