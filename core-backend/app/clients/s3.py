from typing import Any

import boto3

from app.core.config import settings


class S3Client:

    def __init__(self):
        self.bucket_name = settings.s3_bucket_name
        self.region = settings.aws_region

        self.client = boto3.client(
            "s3",
            region_name=self.region,
        )

    # ============================================================
    # UPLOAD FILE
    # ============================================================

    def upload_file(
        self,
        *,
        file_bytes: bytes,
        key: str,
        content_type: str,
    ) -> None:

        self.client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )

    # ============================================================
    # OBJECT URL
    # ============================================================

    def get_object_url(
        self,
        *,
        key: str,
    ) -> str:

        return (
            f"https://{self.bucket_name}.s3."
            f"{self.region}.amazonaws.com/{key}"
        )

    # ============================================================
    # DOWNLOAD URL
    # ============================================================

    def generate_download_url(
        self,
        *,
        key: str,
        expires_in: int = 3600,
    ) -> str:

        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": key,
            },
            ExpiresIn=expires_in,
        )

    # ============================================================
    # DELETE FILE
    # ============================================================

    def delete_object(
        self,
        *,
        key: str,
    ) -> None:

        self.client.delete_object(
            Bucket=self.bucket_name,
            Key=key,
        )

    # ============================================================
    # CHECK FILE
    # ============================================================

    def head_object(
        self,
        *,
        key: str,
    ) -> dict[str, Any]:

        return self.client.head_object(
            Bucket=self.bucket_name,
            Key=key,
        )