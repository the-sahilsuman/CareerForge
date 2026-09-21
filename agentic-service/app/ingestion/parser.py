from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from app.core.logging import get_logger
from app.ingestion.models import ParsedDocument


logger = get_logger(__name__)


class DocumentParser:
    """
    Parse supported document formats into plain text.

    Keeping parsing isolated makes it possible to add:
        DOCX
        TXT
        HTML
        etc.

    later without changing the ingestion pipeline.
    """

    def parse(
        self,
        file_path: str,
        *,
        source_key: str,
        metadata: dict | None = None,
    ) -> ParsedDocument:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document does not exist: {file_path}"
            )

        suffix = path.suffix.lower()

        if suffix == ".pdf":
            text = self._parse_pdf(path)

        elif suffix == ".txt":
            text = path.read_text(
                encoding="utf-8",
            )

        else:
            raise ValueError(
                f"Unsupported document type: {suffix}"
            )

        text = self._clean_text(text)

        if not text:
            raise ValueError(
                f"No text extracted from: {file_path}"
            )

        logger.info(
            "Parsed document: %s",
            source_key,
        )

        return ParsedDocument(
            text=text,
            source_key=source_key,
            metadata=metadata or {},
        )

    # ========================================================
    # PDF
    # ========================================================

    @staticmethod
    def _parse_pdf(
        path: Path,
    ) -> str:

        reader = PdfReader(
            str(path),
        )

        pages: list[str] = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            page_text = page.extract_text() or ""

            if page_text.strip():
                pages.append(
                    f"\n[Page {page_number}]\n"
                    f"{page_text}"
                )

        return "\n".join(pages)

    # ========================================================
    # Cleaning
    # ========================================================

    @staticmethod
    def _clean_text(
        text: str,
    ) -> str:

        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        cleaned_lines: list[str] = []

        previous_blank = False

        for line in lines:

            if not line:
                if not previous_blank:
                    cleaned_lines.append("")

                previous_blank = True
                continue

            cleaned_lines.append(line)
            previous_blank = False

        return "\n".join(
            cleaned_lines
        ).strip()


document_parser = DocumentParser()