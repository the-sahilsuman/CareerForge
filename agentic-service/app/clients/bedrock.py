from __future__ import annotations

import json
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class BedrockClient:
    """
    AWS Bedrock Runtime client.

    This class is intentionally kept as a low-level client.

    LLM-specific behaviour belongs in:
        app/llm/

    Embedding-specific behaviour belongs in:
        app/embeddings/

    This client only handles communication with Bedrock.
    """

    def __init__(
        self,
        region_name: str | None = None,
    ) -> None:

        self.region_name = (
            region_name
            or settings.bedrock_aws_region
            or settings.aws_region
        )

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=self.region_name,
        )

    # ========================================================
    # Raw Invoke Model
    # ========================================================

    def invoke_model(
        self,
        *,
        model_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Invoke a Bedrock model and return decoded JSON.
        """

        try:
            response = self.client.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )

            response_body = response["body"].read()

            return json.loads(response_body)

        except (BotoCoreError, ClientError):
            logger.exception(
                "Bedrock model invocation failed: %s",
                model_id,
            )
            raise

    # ========================================================
    # Converse API
    # ========================================================

    def converse(
        self,
        *,
        model_id: str,
        messages: list[dict[str, Any]],
        system: list[dict[str, str]] | None = None,
        inference_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Invoke a Bedrock model through the Converse API.

        This will be the preferred path for chat LLMs where
        the selected model supports Converse.
        """

        kwargs: dict[str, Any] = {
            "modelId": model_id,
            "messages": messages,
        }

        if system:
            kwargs["system"] = system

        if inference_config:
            kwargs["inferenceConfig"] = inference_config

        try:
            return self.client.converse(**kwargs)

        except (BotoCoreError, ClientError):
            logger.exception(
                "Bedrock Converse invocation failed: %s",
                model_id,
            )
            raise

    # ========================================================
    # Embeddings
    # ========================================================

    def generate_embedding(
        self,
        *,
        text: str,
        model_id: str | None = None,
    ) -> list[float]:
        """
        Generate an embedding using a Bedrock embedding model.

        Amazon Titan Text Embeddings V2 uses:
            {"inputText": "..."}
        """

        selected_model_id = (
            model_id
            or settings.bedrock_embedding_model_id
        )

        response = self.invoke_model(
            model_id=selected_model_id,
            body={
                "inputText": text,
            },
        )

        embedding = response.get("embedding")

        if not embedding:
            raise RuntimeError(
                "Bedrock embedding response did not contain "
                "'embedding'."
            )

        return embedding

    def check_connection(self) -> None:
        """
        Verify that the Bedrock Runtime client can communicate
        with AWS.

        list_foundation_models is not used because this client
        is scoped to the runtime API.
        """

        try:
            self.client.list_foundation_models()

            logger.info(
                "AWS Bedrock connection successful."
            )

        except (BotoCoreError, ClientError):
            logger.exception(
                "AWS Bedrock connection check failed."
            )
            raise


# Shared Bedrock client.
bedrock_client = BedrockClient()