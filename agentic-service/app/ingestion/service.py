from __future__ import annotations

import tempfile
from pathlib import Path

from app.clients.s3 import s3_client
from app.core.logging import get_logger
from app.ingestion.models import IngestionMessage, IngestionResult
from app.ingestion.parser import document_parser
from app.ingestion.processor import ingestion_processor


logger = get_logger(__name__)


class IngestionService:
    """
    High-level ingestion service.

    Responsible for:
        1. Downloading the source document from S3
        2. Parsing the document into text
        3. Passing the parsed document to the ingestion processor
    """

    def process(
        self,
        message: IngestionMessage,
    ) -> IngestionResult:
        suffix = Path(message.s3_key).suffix or ".tmp"

        with tempfile.TemporaryDirectory(
            prefix="careerforge-ingestion-"
        ) as temp_dir:

            local_path = Path(temp_dir) / f"document{suffix}"

            # ========================================================
            # Download from S3
            # ========================================================

            s3_client.download_file(
                message.s3_key,
                str(local_path),
            )

            # ========================================================
            # Parse document
            # ========================================================

            parsed_document = document_parser.parse(
                str(local_path),
                source_key=message.s3_key,
                metadata={
                    "user_id": str(message.user_id),
                    "document_id": str(message.document_id),
                },
            )

            # ========================================================
            # Process parsed document
            # ========================================================

            result = ingestion_processor.process_parsed_document(
                document=parsed_document,
                user_id=str(message.user_id),
                document_id=str(message.document_id),
            )

            return result


ingestion_service = IngestionService()