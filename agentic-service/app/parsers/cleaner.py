import re


def clean_text(
    text: str,
) -> str:

    if not text:
        return ""

    # Normalize line endings
    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    # Remove excessive whitespace
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # Maximum two consecutive newlines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()