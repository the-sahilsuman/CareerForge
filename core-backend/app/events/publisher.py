from typing import Any
from uuid import UUID

from app.clients.sqs import sqs_client
from app.core.config import settings


class EventPublisher:
    def publish(
        self,
        event: dict[str, Any],
        *,
        message_group_id: str | None = None,
        deduplication_id: UUID | None = None,
    ) -> None:
        if not settings.ingestion_queue_url:
            raise RuntimeError(
                "INGESTION_QUEUE_URL is not configured"
            )

        sqs_client.send_message(
            queue_url=settings.ingestion_queue_url,
            message=event,
            message_group_id=message_group_id,
            deduplication_id=(
                str(deduplication_id)
                if deduplication_id
                else None
            ),
        )


event_publisher = EventPublisher()