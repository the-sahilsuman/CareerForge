import asyncio

from app.agent import (
    AgentRequest,
    agent_service,
)
from app.embeddings import get_embedding_provider
from app.memory import session_manager
from app.vectorstore import s3_vector_store


USER_ID = "section9-test-user"
DOCUMENT_ID = "section9-resume"
JD_ID = "section9-jd"


# ============================================================
# Test resume content
# ============================================================

RESUME_CHUNKS = [
    {
        "chunk_id": "chunk-001",
        "text": (
            "Backend engineering experience with Python and FastAPI. "
            "Built REST APIs using FastAPI and Uvicorn. "
            "Implemented asynchronous API endpoints, request validation, "
            "authentication and service-layer architecture."
        ),
    },
    {
        "chunk_id": "chunk-002",
        "text": (
            "Database experience with PostgreSQL and SQLAlchemy. "
            "Worked with PostgreSQL on AWS RDS, database migrations "
            "using Alembic, asynchronous database access using asyncpg, "
            "and relational data modelling."
        ),
    },
    {
        "chunk_id": "chunk-003",
        "text": (
            "Cloud and DevOps experience with AWS, Docker and Linux. "
            "Worked with EC2, S3, IAM, VPC, Route53, Application Load "
            "Balancer, Auto Scaling and CloudWatch. "
            "Built Docker and Docker Compose based deployments."
        ),
    },
    {
        "chunk_id": "chunk-004",
        "text": (
            "Additional engineering experience includes Git and GitHub, "
            "Jenkins CI/CD, Kubernetes, Nginx, Prometheus and Grafana. "
            "Designed deployment pipelines and monitored backend services."
        ),
    },
]


async def seed_resume() -> list[str]:
    """
    Generate embeddings for the test resume and insert them
    into the configured S3 Vector index.
    """

    print()
    print("Seeding test resume into S3 Vectors...")

    embedding_provider = get_embedding_provider()

    vectors = []
    keys = []

    for chunk in RESUME_CHUNKS:

        print(
            f"Embedding {chunk['chunk_id']}..."
        )

        vector = embedding_provider.embed_query(
            chunk["text"]
        )

        print(
            f"  Dimensions: {len(vector)}"
        )

        # Section 3 established that the S3 Vector index
        # is configured for 1024 dimensions.
        if len(vector) != 1024:
            raise ValueError(
                "Resume embedding dimension mismatch: "
                f"expected 1024, got {len(vector)}"
            )

        key = (
            f"resume:"
            f"{USER_ID}:"
            f"{DOCUMENT_ID}:"
            f"{chunk['chunk_id']}"
        )

        vectors.append(
            {
                "key": key,
                "data": {
                    "float32": vector,
                },
                "metadata": {
                    "user_id": USER_ID,
                    "document_id": DOCUMENT_ID,
                    "chunk_id": chunk["chunk_id"],
                    "source": "section9-test-resume",
                    "text": chunk["text"],
                },
            }
        )

        keys.append(key)

    s3_vector_store.upsert(
        vectors
    )

    print(
        f"Inserted {len(vectors)} resume chunks."
    )

    return keys


async def main() -> None:

    print()
    print("=" * 70)
    print("SECTION 9 - RETRIEVAL + AGENT TEST")
    print("=" * 70)

    inserted_keys: list[str] = []

    try:

        # ----------------------------------------------------
        # Create test session
        # ----------------------------------------------------

        print("\nCreating session...")

        await session_manager.get_or_create(
            USER_ID
        )

        # ----------------------------------------------------
        # Add test JD
        # ----------------------------------------------------

        print("Adding JD...")

        await session_manager.add_jd(
            user_id=USER_ID,
            jd_id=JD_ID,
            title="Python Backend Engineer",
            company="CareerForge Test",
            description=(
                "Looking for a Python backend engineer "
                "with FastAPI, PostgreSQL, AWS and Docker."
            ),
        )

        # ----------------------------------------------------
        # Seed resume
        # ----------------------------------------------------

        inserted_keys = await seed_resume()

        # ----------------------------------------------------
        # Ask agent
        # ----------------------------------------------------

        question = (
            "What skills from my resume are relevant "
            "to this backend engineering role?"
        )

        print()
        print("USER:")
        print(question)

        response = await agent_service.chat(
            AgentRequest(
                user_id=USER_ID,
                message=question,
                jd_id=JD_ID,
            )
        )

        # ----------------------------------------------------
        # Output
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("AGENT RESPONSE")
        print("=" * 70)

        print(response.message)

        print()
        print(
            "Retrieved chunks:",
            response.retrieved_chunks,
        )

        print(
            "JD:",
            response.jd_id,
        )

        print("=" * 70)

        # ----------------------------------------------------
        # Verify session
        # ----------------------------------------------------

        session = (
            await session_manager.get_session(
                USER_ID
            )
        )

        print()
        print(
            "Stored messages:",
            len(session.messages),
        )

        # ----------------------------------------------------
        # Basic assertions
        # ----------------------------------------------------

        if response.jd_id != JD_ID:
            raise AssertionError(
                "Agent response contains incorrect JD ID."
            )

        if response.retrieved_chunks <= 0:
            raise AssertionError(
                "Retrieval returned zero chunks. "
                "Section 9 retrieval test failed."
            )

        if len(session.messages) < 2:
            raise AssertionError(
                "Expected user and assistant messages "
                "to be stored in the session."
            )

        print()
        print("=" * 70)
        print("SECTION 9 PASSED")
        print("=" * 70)

    finally:

        # ----------------------------------------------------
        # Delete temporary test vectors
        # ----------------------------------------------------

        if inserted_keys:

            print()
            print(
                "Deleting test resume vectors..."
            )

            s3_vector_store.delete(
                inserted_keys
            )

            print(
                "Test resume vectors deleted."
            )

        # ----------------------------------------------------
        # Delete Redis test session
        # ----------------------------------------------------

        await session_manager.delete_session(
            USER_ID
        )

        print(
            "Test session deleted."
        )


if __name__ == "__main__":
    asyncio.run(main())