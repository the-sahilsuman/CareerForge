import asyncio
import os
from urllib.parse import urlparse

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings


class S3ResumeStorage:
    """
    Handles resume files stored in Amazon S3.
    """

    def __init__(self) -> None:
        self.bucket_name = (
            settings.resume_s3_bucket_name
        )

        self.client = boto3.client(
            "s3",
            region_name=settings.aws_region,
        )

    async def download_resume(
        self,
        s3_url: str,
        destination: str,
    ) -> str:

        bucket, key = self._parse_s3_url(
            s3_url
        )

        await asyncio.to_thread(
            self.client.download_file,
            bucket,
            key,
            destination,
        )

        return destination

    @staticmethod
    def _parse_s3_url(
        s3_url: str,
    ) -> tuple[str, str]:

        parsed = urlparse(s3_url)

        # s3://bucket/key
        if parsed.scheme == "s3":
            return (
                parsed.netloc,
                parsed.path.lstrip("/"),
            )

        # https://bucket.s3.amazonaws.com/key
        if ".s3." in parsed.netloc or ".s3-" in parsed.netloc:
            bucket = parsed.netloc.split(".s3")[0]
            key = parsed.path.lstrip("/")

            return bucket, key

        raise ValueError(
            f"Unsupported S3 URL: {s3_url}"
        )


async def check_s3_connection(
    bucket_name: str | None = None,
) -> None:

    bucket = (
        bucket_name
        or settings.resume_s3_bucket_name
    )

    client = boto3.client(
        "s3",
        region_name=settings.aws_region,
    )

    try:
        await asyncio.to_thread(
            client.head_bucket,
            Bucket=bucket,
        )

    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(
            f"S3 bucket '{bucket}' is not reachable."
        ) from exc