import asyncio

import fitz


def _parse_pdf_sync(
    file_path: str,
) -> str:

    document = fitz.open(file_path)

    try:
        pages = []

        for page in document:
            text = page.get_text()

            if text:
                pages.append(text)

        return "\n\n".join(pages)

    finally:
        document.close()


async def parse_pdf(
    file_path: str,
) -> str:

    return await asyncio.to_thread(
        _parse_pdf_sync,
        file_path,
    )