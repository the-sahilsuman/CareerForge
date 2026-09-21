from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CognitoJWTError, verify_access_token
from app.db.session import get_db
from app.models.enums import UserRole, UserStatus
from app.models.user import User

from app.core.config import settings


bearer_scheme = HTTPBearer(
    auto_error=False,
)


@dataclass(frozen=True)
class CurrentUser:
    id: UUID
    user_id: str
    cognito_sub: str
    login_email: str
    role: UserRole
    status: UserStatus


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        payload = verify_access_token(
            credentials.credentials
        )
    except CognitoJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    cognito_sub = payload["sub"]

    result = await db.execute(
        select(User).where(
            User.cognito_sub == cognito_sub
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
        )

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active.",
        )

    return CurrentUser(
        id=user.id,
        user_id=user.user_id,
        cognito_sub=user.cognito_sub,
        login_email=user.login_email,
        role=user.role,
        status=user.status,
    )


def require_roles(
    *allowed_roles: UserRole,
) -> Callable:

    async def dependency(
        current_user: CurrentUser = Depends(
            get_current_user
        ),
    ) -> CurrentUser:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )

        return current_user

    return dependency

# ============================================================
# INTERNAL AGENTIC SERVICE AUTHENTICATION
# ============================================================


async def verify_agentic_service(
    service_key: str | None = Header(
        default=None,
        alias="X-CareerForge-Service-Key",
    ),
) -> None:
    """
    Authenticate internal requests coming from Agentic Service.

    This endpoint is never called directly by the browser.

    Agentic Service must provide the same shared internal
    service key configured in Core Backend.
    """

    if not service_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Internal service authentication required.",
        )

    if service_key != settings.agentic_internal_service_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal service credentials.",
        )