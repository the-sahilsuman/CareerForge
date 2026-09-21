import asyncio
import logging
import socket
from uuid import UUID

from app.clients.sqs import sqs_client
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.repositories.outbox import OutboxRepository


logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(self) -> None:
        self.worker_id = socket.gethostname()

    async def process_batch(self) -> None:
        if not settings.ingestion_queue_url:
            logger.warning(
                "INGESTION_QUEUE_URL is not configured"
            )
            return

        async with AsyncSessionLocal() as session:
            repository = OutboxRepository(session)

            events = await repository.get_pending(limit=100)

            for event in events:
                try:
                    await repository.mark_processing(
                        event,
                        self.worker_id,
                    )

                    await session.commit()

                    response = sqs_client.send_message(
                        queue_url=settings.ingestion_queue_url,
                        message={
                            "event_id": str(event.id),
                            "event_type": event.event_type,
                            "aggregate_type": event.aggregate_type,
                            "aggregate_id": str(event.aggregate_id),
                            "payload": event.payload,
                        },
                    )

                    logger.info(
                        "Published outbox event",
                        extra={
                            "event_id": str(event.id),
                            "event_type": event.event_type,
                            "message_id": response.get("MessageId"),
                        },
                    )

                    async with AsyncSessionLocal() as update_session:
                        update_repository = OutboxRepository(
                            update_session
                        )

                        result_event = await update_session.get(
                            type(event),
                            event.id,
                        )

                        if result_event:
                            await update_repository.mark_published(
                                result_event
                            )
                            await update_session.commit()

                except Exception as exc:
                    logger.exception(
                        "Failed to publish outbox event",
                        extra={
                            "event_id": str(event.id),
                            "event_type": event.event_type,
                        },
                    )

                    retry_delay = min(
                        2 ** min(event.attempts, 8),
                        300,
                    )

                    async with AsyncSessionLocal() as retry_session:
                        retry_repository = OutboxRepository(
                            retry_session
                        )

                        retry_event = await retry_session.get(
                            type(event),
                            event.id,
                        )

                        if retry_event:
                            await retry_repository.mark_failed(
                                retry_event,
                                str(exc),
                                retry_delay,
                            )
                            await retry_session.commit()

    async def run(self) -> None:
        logger.info(
            "Starting outbox worker: %s",
            self.worker_id,
        )

        try:
            while True:
                try:
                    await self.process_batch()
                except Exception:
                    logger.exception(
                        "Unexpected outbox worker error"
                    )

                await asyncio.sleep(5)

        except asyncio.CancelledError:
            logger.info(
                "Outbox worker cancelled: %s",
                self.worker_id,
            )
            raise


worker = OutboxWorker()


if __name__ == "__main__":
    asyncio.run(worker.run())
