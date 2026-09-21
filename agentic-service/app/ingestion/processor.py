from __future__ import annotations

from app.core.logging import get_logger
from app.embeddings import get_embedding_provider
from app.ingestion.chunker import document_chunker
from app.ingestion.models import (
    IngestionMessage,
    IngestionResult,
)
from app.ingestion.parser import document_parser
from app.vectorstore import s3_vector_store
from app.ingestion.models import ParsedDocument


logger = get_logger(__name__)


class IngestionProcessor:
    """
    Complete document ingestion pipeline.

    Flow:

        S3 document
            ↓
        Parse
            ↓
        Clean
            ↓
        Chunk
            ↓
        Embed
            ↓
        S3 Vectors
    """

    def __init__(self) -> None:

        self.embedding_provider = (
            get_embedding_provider()
        )

    def process_parsed_document(
        self,
        *,
        document: ParsedDocument,
        user_id: str,
        document_id: str,
    ) -> IngestionResult:

        logger.info(
            "Starting parsed-document ingestion: "
            "user=%s document=%s",
            user_id,
            document_id,
        )

        chunks = document_chunker.chunk(
            document,
            user_id=user_id,
            document_id=document_id,
        )

        if not chunks:
            raise ValueError(
                "Document produced zero chunks."
            )

        texts = [
            chunk.text
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_provider.embed_documents(
                texts
            )
        )

        if len(embeddings) != len(chunks):
            raise RuntimeError(
                "Embedding count does not match "
                "chunk count."
            )

        vectors = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):
            vector_key = (
                f"user:{chunk.user_id}"
                f":document:{chunk.document_id}"
                f":chunk:{chunk.chunk_id}"
            )

            vectors.append(
                {
                    "key": vector_key,
                    "data": {
                        "float32": embedding,
                    },
                    "metadata": {
                        **chunk.metadata,
                        "user_id": chunk.user_id,
                        "document_id": chunk.document_id,
                        "chunk_id": chunk.chunk_id,
                        "text": chunk.text,
                    },
                }
            )

        s3_vector_store.upsert(vectors)

        logger.info(
            "Completed parsed-document ingestion: "
            "user=%s document=%s chunks=%d vectors=%d",
            user_id,
            document_id,
            len(chunks),
            len(vectors),
        )

        return IngestionResult(
            user_id=user_id,
            document_id=document_id,
            chunks_created=len(chunks),
            vectors_created=len(vectors),
        )


ingestion_processor = IngestionProcessor()