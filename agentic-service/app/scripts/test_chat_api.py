from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


USER_ID = "section13-api-test-user"


def main() -> None:

    print()
    print("=" * 70)
    print("SECTION 13 - CHAT API TEST")
    print("=" * 70)

    with TestClient(app) as client:

        # ====================================================
        # Health
        # ====================================================

        print()
        print("Testing /health...")

        health_response = client.get(
            "/health",
        )

        print(
            "Status:",
            health_response.status_code,
        )

        print(
            "Response:",
            health_response.json(),
        )

        assert health_response.status_code == 200

        # ====================================================
        # Chat endpoint existence
        # ====================================================

        print()
        print("Testing /api/v1/chat...")

        response = client.post(
            "/api/v1/chat",
            json={
                "user_id": USER_ID,
                "message": "Hello CareerForge.",
            },
        )

        print(
            "Status:",
            response.status_code,
        )

        print(
            "Response:",
            response.json(),
        )

        assert response.status_code == 200

        data = response.json()

        assert "message" in data
        assert data["message"]

        assert data["user_id"] == USER_ID

        assert "jd_id" in data

        assert "retrieved_chunks" in data

        assert "metadata" in data

    print()
    print("=" * 70)
    print("SECTION 13 PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()