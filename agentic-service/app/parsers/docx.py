import asyncio

from docx import Document


def _parse_docx_sync(
    file_path: str,
) -> str:

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


async def parse_docx(
    file_path: str,
) -> str:

    return await asyncio.to_thread(
        _parse_docx_sync,
        file_path,
    )