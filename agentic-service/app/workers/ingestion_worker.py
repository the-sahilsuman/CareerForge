from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings
from app.core.logging import get_logger
from app.ingestion.models import IngestionMessage
from app.ingestion.service import ingestion_service


logger = get_logger(__name__)


class IngestionWorker:
    """
    Long-running SQS ingestion worker.

    Critical rule:

        SUCCESS
            → delete SQS message

        FAILURE
            → DO NOT delete message

    This allows SQS visibility timeout/redelivery to handle
    transient failures.
    """

    def __init__(self) -> None:

        if not settings.ingestion_queue_url:
            raise RuntimeError(
                "INGESTION_QUEUE_URL is not configured."
            )

        self.queue_url = (
            settings.ingestion_queue_url
        )

        self.client = boto3.client(
            "sqs",
            region_name=settings.aws_region,
        )

        self.running = True

    # ========================================================
    # Message parsing
    # ========================================================

    @staticmethod
    def _parse_message(
        body: str,
    ) -> dict[str, Any]:

        payload: dict[str, Any] = json.loads(
            body
        )

        if "event_id" not in payload:
            raise ValueError(
                "Missing event_id in SQS event."
            )

        if "event_type" not in payload:
            raise ValueError(
                "Missing event_type in SQS event."
            )

        if "payload" not in payload:
            raise ValueError(
                "Missing payload in SQS event."
            )

        event_payload = payload["payload"]

        if not isinstance(
            event_payload,
            dict,
        ):
            raise ValueError(
                "Event payload must be an object."
            )

        return payload


    async def _process_profile(
        self,
        *,
        user_id: str,
    ) -> None:

        from app.ingestion.user_data import (
            user_data_ingestion_service,
        )

        await user_data_ingestion_service.process_profile(
            user_id=user_id,
        )

    async def _process_resume(
        self,
        *,
        user_id: str,
        operation: str,
    ) -> None:

        from app.ingestion.user_data import (
            user_data_ingestion_service,
        )

        await user_data_ingestion_service.process_resume(
            user_id=user_id,
            operation=operation,
        )

    # ========================================================
    # Process one message
    # ========================================================

    def process_message(
        self,
        message: dict[str, Any],
    ) -> None:

        receipt_handle = message[
            "ReceiptHandle"
        ]

        body = message[
            "Body"
        ]

        try:

            event = self._parse_message(body)

            event_id = event["event_id"]
            event_type = event["event_type"]
            payload = event["payload"]

            user_id = payload["user_id"]
            resource = payload["resource"]
            operation = payload["operation"]

            logger.info(
                "Received ingestion event: "
                "event=%s type=%s resource=%s "
                "operation=%s user=%s",
                event_id,
                event_type,
                resource,
                operation,
                user_id,
            )

            # --------------------------------------------------
            # Resume
            # --------------------------------------------------

            if resource == "resume":

                asyncio.run(
                    self._process_resume(
                        user_id=user_id,
                        operation=operation,
                    )
                )

            # --------------------------------------------------
            # Profile / skills / projects / etc.
            # --------------------------------------------------

            else:

                asyncio.run(
                    self._process_profile(
                        user_id=user_id,
                    )
                )

            # --------------------------------------------------
            # SUCCESS
            # --------------------------------------------------

            self.client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
            )

            logger.info(
                "Successfully processed ingestion event: %s",
                event_id,
            )

        except Exception:

            logger.exception(
                "Ingestion failed. "
                "Message will remain in SQS for retry."
            )
            # IMPORTANT:
            # Do NOT delete the message.

    # ========================================================
    # Poll
    # ========================================================

    def run(self) -> None:

        logger.info(
            "Starting ingestion worker."
        )

        while self.running:

            try:

                response = (
                    self.client.receive_message(
                        QueueUrl=self.queue_url,
                        MaxNumberOfMessages=(
                            settings.sqs_max_messages
                        ),
                        WaitTimeSeconds=(
                            settings.sqs_wait_time_seconds
                        ),
                        VisibilityTimeout=(
                            settings.sqs_visibility_timeout
                        ),
                    )
                )

                messages = response.get(
                    "Messages",
                    [],
                )

                if not messages:
                    continue

                for message in messages:

                    self.process_message(
                        message,
                    )

            except (BotoCoreError, ClientError):

                logger.exception(
                    "SQS polling failed."
                )

                time.sleep(
                    settings.sqs_error_retry_seconds
                )

            except Exception:

                logger.exception(
                    "Unexpected worker error."
                )

                time.sleep(
                    settings.sqs_error_retry_seconds
                )

    def stop(self) -> None:

        self.running = False


def main() -> None:

    worker = IngestionWorker()

    try:
        worker.run()

    except KeyboardInterrupt:

        logger.info(
            "Stopping ingestion worker..."
        )

        worker.stop()


if __name__ == "__main__":
    main()