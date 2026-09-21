from __future__ import annotations

from typing import BinaryIO

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class S3Client:
    """
    Thin wrapper around the AWS S3 client.

    Responsibilities:
    - Download objects
    - Upload objects
    - Check object existence
    - Generate object URLs/keys

    Business logic should NOT directly create boto3 clients.
    """

    def __init__(
        self,
        bucket_name: str | None = None,
    ) -> None:
        self.bucket_name = (
            bucket_name
            or settings.resume_s3_bucket_name
            or settings.s3_bucket
        )

        self.client = boto3.client(
            "s3",
            region_name=settings.aws_region,
        )

    def _require_bucket(self) -> str:
        """
        Ensure an S3 bucket has been configured.
        """

        if not self.bucket_name:
            raise RuntimeError(
                "S3 bucket is not configured. "
                "Set RESUME_S3_BUCKET_NAME or S3_BUCKET."
            )

        return self.bucket_name

    # ========================================================
    # Upload
    # ========================================================

    def upload_file(
        self,
        file_path: str,
        key: str,
        *,
        content_type: str | None = None,
    ) -> str:
        """
        Upload a local file to S3.

        Returns:
            S3 object key.
        """

        bucket = self._require_bucket()

        extra_args: dict[str, str] = {}

        if content_type:
            extra_args["ContentType"] = content_type

        try:
            if extra_args:
                self.client.upload_file(
                    file_path,
                    bucket,
                    key,
                    ExtraArgs=extra_args,
                )
            else:
                self.client.upload_file(
                    file_path,
                    bucket,
                    key,
                )

            logger.info(
                "Uploaded S3 object: s3://%s/%s",
                bucket,
                key,
            )

            return key

        except (BotoCoreError, ClientError):
            logger.exception(
                "Failed to upload S3 object: s3://%s/%s",
                bucket,
                key,
            )
            raise

    # ========================================================
    # Upload bytes
    # ========================================================

    def put_object(
        self,
        body: bytes | BinaryIO,
        key: str,
        *,
        content_type: str | None = None,
    ) -> str:
        """
        Upload bytes/file-like object to S3.
        """

        bucket = self._require_bucket()

        kwargs = {
            "Bucket": bucket,
            "Key": key,
            "Body": body,
        }

        if content_type:
            kwargs["ContentType"] = content_type

        try:
            self.client.put_object(**kwargs)

            logger.info(
                "Stored S3 object: s3://%s/%s",
                bucket,
                key,
            )

            return key

        except (BotoCoreError, ClientError):
            logger.exception(
                "Failed to store S3 object: s3://%s/%s",
                bucket,
                key,
            )
            raise

    # ========================================================
    # Download
    # ========================================================

    def download_file(
        self,
        key: str,
        destination_path: str,
    ) -> None:
        """
        Download an S3 object to a local path.
        """

        bucket = self._require_bucket()

        try:
            self.client.download_file(
                bucket,
                key,
                destination_path,
            )

            logger.info(
                "Downloaded S3 object: s3://%s/%s",
                bucket,
                key,
            )

        except (BotoCoreError, ClientError):
            logger.exception(
                "Failed to download S3 object: s3://%s/%s",
                bucket,
                key,
            )
            raise

    # ========================================================
    # Get object bytes
    # ========================================================

    def get_object_bytes(
        self,
        key: str,
    ) -> bytes:
        """
        Download an S3 object directly into memory.
        """

        bucket = self._require_bucket()

        try:
            response = self.client.get_object(
                Bucket=bucket,
                Key=key,
            )

            return response["Body"].read()

        except (BotoCoreError, ClientError):
            logger.exception(
                "Failed to read S3 object: s3://%s/%s",
                bucket,
                key,
            )
            raise

    # ========================================================
    # Head object
    # ========================================================

    def object_exists(
        self,
        key: str,
    ) -> bool:
        """
        Check whether an object exists.
        """

        bucket = self._require_bucket()

        try:
            self.client.head_object(
                Bucket=bucket,
                Key=key,
            )

            return True

        except ClientError as exc:
            error_code = exc.response.get(
                "Error",
                {},
            ).get(
                "Code"
            )

            if error_code in {
                "404",
                "NoSuchKey",
                "NotFound",
            }:
                return False

            logger.exception(
                "Failed checking S3 object: s3://%s/%s",
                bucket,
                key,
            )
            raise

    # ========================================================
    # Delete
    # ========================================================

    def delete_object(
        self,
        key: str,
    ) -> None:
        """
        Delete an S3 object.
        """

        bucket = self._require_bucket()

        try:
            self.client.delete_object(
                Bucket=bucket,
                Key=key,
            )

            logger.info(
                "Deleted S3 object: s3://%s/%s",
                bucket,
                key,
            )

        except (BotoCoreError, ClientError):
            logger.exception(
                "Failed deleting S3 object: s3://%s/%s",
                bucket,
                key,
            )
            raise

    # ========================================================
    # Presigned URL
    # ========================================================

    def generate_presigned_url(
        self,
        key: str,
        *,
        expiration: int = 3600,
    ) -> str:
        """
        Generate a temporary presigned GET URL.
        """

        bucket = self._require_bucket()

        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": bucket,
                    "Key": key,
                },
                ExpiresIn=expiration,
            )

        except (BotoCoreError, ClientError):
            logger.exception(
                "Failed generating presigned URL: "
                "s3://%s/%s",
                bucket,
                key,
            )
            raise

    def check_connection(self) -> None:
        """
        Verify that the configured S3 bucket is accessible.
        """

        bucket = self._require_bucket()

        try:
            self.client.head_bucket(
                Bucket=bucket,
            )

            logger.info(
                "S3 bucket is accessible: %s",
                bucket,
            )

        except (BotoCoreError, ClientError):
            logger.exception(
                "S3 bucket is not accessible: %s",
                bucket,
            )
            raise


# Shared client instance.
s3_client = S3Client()