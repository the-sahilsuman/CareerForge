from __future__ import annotations

import asyncio


async def test_llm() -> None:

    from app.agent.llm import (
        get_llm_provider,
    )

    print()
    print("=" * 72)
    print("OPENROUTER LLM TEST")
    print("=" * 72)

    llm = get_llm_provider()

    response = await llm.generate(
        system_prompt=(
            "You are a concise career assistant."
        ),
        user_prompt=(
            "In one sentence, explain "
            "what RAG means."
        ),
    )

    print()
    print("LLM RESPONSE:")
    print(response)


def test_embedding() -> None:

    from app.embeddings import (
        get_embedding_provider,
    )

    print()
    print("=" * 72)
    print("OPENROUTER EMBEDDING TEST")
    print("=" * 72)

    provider = get_embedding_provider()

    vector = provider.embed_text(
        "Python backend engineering "
        "and AWS cloud development.",
        task_type="RETRIEVAL_DOCUMENT",
    )

    print()
    print(
        f"Embedding dimension: {len(vector)}"
    )

    if len(vector) != 1024:

        raise RuntimeError(
            "Unexpected embedding dimension."
        )

    print(
        "Embedding provider test passed."
    )


async def main() -> None:

    await test_llm()

    test_embedding()

    print()
    print("=" * 72)
    print("OPENROUTER TEST PASSED")
    print("=" * 72)
    print()


if __name__ == "__main__":

    asyncio.run(main())