from urllib.parse import quote
from datetime import datetime
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from fastapi.responses import RedirectResponse

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
    verify_agentic_service,
)
from app.api.repository_dependencies import (
    get_email_connection_service,
)
from app.core.config import settings
from app.core.errors import ValidationError
from app.schemas.email import EmailConnectionResponse
from app.services.email_connection import (
    EmailConnectionService,
)


router = APIRouter(
    prefix="/email-connections",
    tags=["Email Connections"],
)


# ============================================================
# LIST CONNECTIONS
# ============================================================

@router.get(
    "",
    response_model=list[EmailConnectionResponse],
)
async def list_email_connections(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: EmailConnectionService = Depends(
        get_email_connection_service
    ),
):
    return await service.get_connections(
        current_user.id
    )


# ============================================================
# START GOOGLE OAUTH
# ============================================================

@router.get(
    "/google",
)
async def get_google_authorization_url(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: EmailConnectionService = Depends(
        get_email_connection_service
    ),
):
    authorization_url = (
        service.get_google_authorization_url(
            current_user.id
        )
    )

    return {
        "authorization_url": authorization_url
    }


# ============================================================
# GOOGLE OAUTH CALLBACK
# ============================================================

@router.get(
    "/google/callback",
)
async def google_oauth_callback(
    code: str,
    state: str,
    service: EmailConnectionService = Depends(
        get_email_connection_service
    ),
):

    try:

        # ----------------------------------------------------
        # 1. Decode signed OAuth state
        # ----------------------------------------------------

        (
            user_id,
            code_verifier,
        ) = service.decode_google_oauth_state(
            state
        )

        print(
            "Google OAuth state validated."
        )

        print(
            "User ID:",
            user_id,
        )

        # ----------------------------------------------------
        # 2. Exchange authorization code
        # 3. Reuse ORIGINAL PKCE verifier
        # 4. Get Google account email
        # 5. Validate professional email
        # 6. Save/update RDS connection
        # ----------------------------------------------------

        connection = (
            await service.connect_google(
                user_id=user_id,
                code=code,
                code_verifier=code_verifier,
            )
        )

        print(
            "Google Gmail connection created:",
            connection.id,
            connection.email_address,
        )

    except ValidationError as exc:

        print(
            "Google OAuth validation error:",
            repr(exc),
        )

        message = quote(
            str(exc)
        )

        return RedirectResponse(
            url=(
                f"{settings.frontend_url}"
                f"/profile?"
                f"email_connection_error={message}"
            ),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    except Exception as exc:

        print(
            "GOOGLE OAUTH CALLBACK ERROR:",
            repr(exc),
        )

        message = quote(
            f"{type(exc).__name__}: {str(exc)}"
        )

        return RedirectResponse(
            url=(
                f"{settings.frontend_url}"
                f"/profile?"
                f"email_connection_error={message}"
            ),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    return RedirectResponse(
        url=(
            f"{settings.frontend_url}"
            "/profile?email_connection=connected"
        ),
        status_code=status.HTTP_303_SEE_OTHER,
    )

# ============================================================
# INTERNAL GOOGLE TOKEN REFRESH
# ============================================================

@router.post(
    "/internal/{connection_id}/refresh",
)
async def refresh_google_token_for_agentic(
    connection_id: UUID,
    _: None = Depends(
        verify_agentic_service
    ),
    service: EmailConnectionService = Depends(
        get_email_connection_service
    ),
):
    """
    Internal endpoint used ONLY by Agentic Service.

    Agentic Service calls this endpoint when the current
    Google access token has expired.

    Core Backend:
        1. loads the connection
        2. decrypts refresh token
        3. refreshes with Google
        4. updates email_connections
        5. returns the new access token

    The refresh token is NEVER returned.
    """

    return await service.refresh_google_access_token(
        connection_id
    )


# ============================================================
# DISCONNECT
# ============================================================

@router.delete(
    "/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def disconnect_email(
    connection_id: UUID,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: EmailConnectionService = Depends(
        get_email_connection_service
    ),
):
    await service.disconnect(
        user_id=current_user.id,
        connection_id=connection_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )