from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.outbox import OutboxRepository


async def enqueue_user_data_event(
    db: AsyncSession,
    *,
    resource: str,
    operation: str,
    user_id: UUID,
    resource_id: UUID | None = None,
    metadata: dict | None = None,
) -> None:
    """
    Create an outbox event for Agentic Service.

    The event is written using the same DB transaction as
    the source data change.
    """

    aggregate_id = resource_id or user_id

    await OutboxRepository(db).create(
        event_type=f"{resource}.{operation}",
        aggregate_type=resource,
        aggregate_id=aggregate_id,
        payload={
            "user_id": str(user_id),
            "resource": resource,
            "operation": operation,
            "resource_id": (
                str(resource_id)
                if resource_id
                else None
            ),
            "metadata": metadata or {},
        },
    )