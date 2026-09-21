import asyncio
import json
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings


class IngestionQueue:
    """
    Amazon SQS client for CareerForge ingestion events.
    """

    def __init__(self) -> None:

        self.queue_url = (
            settings.ingestion_queue_url
        )

        self.client = boto3.client(
            "sqs",
            region_name=settings.aws_region,
        )

    async def send(
        self,
        *,
        user_id: str,
        event: str = "user_updated",
    ) -> None:

        message = {
            "event": event,
            "user_id": user_id,
        }

        await asyncio.to_thread(
            self._send_sync,
            message,
        )

    def _send_sync(
        self,
        message: dict[str, Any],
    ) -> None:

        try:
            self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(
                    message
                ),
            )

        except (
            ClientError,
            BotoCoreError,
        ) as exc:

            raise RuntimeError(
                "Failed to send ingestion event."
            ) from exc

    async def receive(
        self,
        *,
        max_messages: int = 1,
        wait_time_seconds: int = 20,
    ) -> list[dict[str, Any]]:

        return await asyncio.to_thread(
            self._receive_sync,
            max_messages,
            wait_time_seconds,
        )

    def _receive_sync(
        self,
        max_messages: int,
        wait_time_seconds: int,
    ) -> list[dict[str, Any]]:

        try:
            response = self.client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time_seconds,
                VisibilityTimeout=300,
            )

        except (
            ClientError,
            BotoCoreError,
        ) as exc:

            raise RuntimeError(
                "Failed to receive ingestion messages."
            ) from exc

        messages = []

        for message in response.get(
            "Messages",
            [],
        ):

            try:
                body = json.loads(
                    message["Body"]
                )

                messages.append(
                    {
                        "message_id": message[
                            "MessageId"
                        ],
                        "receipt_handle": message[
                            "ReceiptHandle"
                        ],
                        "body": body,
                    }
                )

            except json.JSONDecodeError:
                # Invalid messages are returned so the
                # worker can decide how to handle them.
                messages.append(
                    {
                        "message_id": message[
                            "MessageId"
                        ],
                        "receipt_handle": message[
                            "ReceiptHandle"
                        ],
                        "body": None,
                    }
                )

        return messages

    async def delete(
        self,
        receipt_handle: str,
    ) -> None:

        await asyncio.to_thread(
            self._delete_sync,
            receipt_handle,
        )

    def _delete_sync(
        self,
        receipt_handle: str,
    ) -> None:

        try:
            self.client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
            )

        except (
            ClientError,
            BotoCoreError,
        ) as exc:

            raise RuntimeError(
                "Failed to delete SQS message."
            ) from exc

    async def health_check(self) -> None:

        await asyncio.to_thread(
            self._health_check_sync
        )

    def _health_check_sync(self) -> None:

        try:
            self.client.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=[
                    "QueueArn",
                ],
            )

        except (
            ClientError,
            BotoCoreError,
        ) as exc:

            raise RuntimeError(
                "Ingestion queue health check failed."
            ) from exc