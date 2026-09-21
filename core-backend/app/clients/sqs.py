import json
from typing import Any

import boto3

from app.core.config import settings


class SQSClient:
    def __init__(self) -> None:
        self.client = boto3.client(
            "sqs",
            region_name=settings.aws_region,
        )

    def send_message(
        self,
        queue_url: str,
        message: dict[str, Any],
        *,
        message_group_id: str | None = None,
        deduplication_id: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "QueueUrl": queue_url,
            "MessageBody": json.dumps(message, default=str),
        }

        if message_group_id:
            params["MessageGroupId"] = message_group_id

        if deduplication_id:
            params["MessageDeduplicationId"] = deduplication_id

        return self.client.send_message(**params)


sqs_client = SQSClient()