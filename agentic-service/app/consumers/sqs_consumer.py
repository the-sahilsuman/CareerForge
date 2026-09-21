import json
import logging
from typing import Any

import boto3

from app.core.config import settings


logger = logging.getLogger(__name__)


class SQSConsumer:
    def __init__(self) -> None:
        self.client = boto3.client(
            "sqs",
            region_name=settings.aws_region,
        )

        self.queue_url = settings.ingestion_queue_url

    def receive_messages(
        self,
        *,
        max_messages: int = 10,
        wait_time_seconds: int = 20,
    ) -> list[dict[str, Any]]:
        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=wait_time_seconds,
        )

        return response.get("Messages", [])

    def delete_message(
        self,
        receipt_handle: str,
    ) -> None:
        self.client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle,
        )

    @staticmethod
    def decode_message(
        body: str,
    ) -> dict[str, Any]:
        return json.loads(body)