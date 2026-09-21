from __future__ import annotations

import asyncio

from app.email import (
    EmailCredentialsError,
    EmailNotConnectedError,
    email_connection_service,
)


USER_ID = "PUT_REAL_USER_UUID_HERE"


async def main() -> None:

    print()
    print("=" * 70)
    print("SECTION 18 - EMAIL CONNECTION CHECK")
    print("=" * 70)

    # ========================================================
    # Connection check
    # ========================================================

    print()
    print("Checking email connection...")

    connection = (
        await email_connection_service.check_connection(
            USER_ID,
        )
    )

    print()
    print("CONNECTED:", connection.connected)
    print("PROVIDER:", connection.provider)
    print(
        "EMAIL:",
        connection.email_address,
    )
    print(
        "CONNECTION ID:",
        connection.connection_id,
    )
    print(
        "EXPIRES AT:",
        connection.expires_at,
    )

    # ========================================================
    # Credentials
    # ========================================================

    if connection.connected:

        print()
        print(
            "Loading OAuth credentials..."
        )

        credentials = (
            await email_connection_service.get_credentials(
                USER_ID,
            )
        )

        print()
        print(
            "Provider:",
            credentials.provider,
        )

        print(
            "Email:",
            credentials.email_address,
        )

        print(
            "Access token loaded:",
            bool(
                credentials.access_token
            ),
        )

        print(
            "Refresh token loaded:",
            bool(
                credentials.refresh_token
            ),
        )

        print(
            "Expires at:",
            credentials.expires_at,
        )

        # Never print the actual token.

        assert credentials.access_token

        print()
        print(
            "OAuth credentials successfully "
            "loaded and decrypted."
        )

    else:

        print()
        print(
            "No active email connection."
        )

    print()
    print("=" * 70)
    print("SECTION 18 PASSED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())