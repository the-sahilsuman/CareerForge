from __future__ import annotations

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from app.core.config import settings
from app.core.logging import get_logger
from app.ingestion.models import (
    DocumentChunk,
    ParsedDocument,
)


logger = get_logger(__name__)


class DocumentChunker:
    """
    Convert parsed documents into retrieval chunks.
    """

    def __init__(self) -> None:

        self.splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
                separators=[
                    "\n\n",
                    "\n",
                    ". ",
                    " ",
                    "",
                ],
            )
        )

    def chunk(
        self,
        document: ParsedDocument,
        *,
        user_id: str,
        document_id: str,
    ) -> list[DocumentChunk]:

        texts = self.splitter.split_text(
            document.text,
        )

        chunks: list[DocumentChunk] = []

        for index, text in enumerate(
            texts,
        ):

            text = text.strip()

            if not text:
                continue

            chunk_id = (
                f"{document_id}:chunk:{index}"
            )

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    text=text,
                    user_id=user_id,
                    document_id=document_id,
                    metadata={
                        **document.metadata,
                        "chunk_index": index,
                        "source": document.source_key,
                    },
                )
            )

        logger.info(
            "Created %d chunks for document %s",
            len(chunks),
            document_id,
        )

        return chunks


document_chunker = DocumentChunker()