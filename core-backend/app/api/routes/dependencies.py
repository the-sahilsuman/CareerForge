from dataclasses import dataclass
from uuid import UUID
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CognitoJWTError, verify_access_token
from app.db.session import get_db
from app.models.user import User


bearer_scheme = HTTPBearer(
    auto_error=False,
)


@dataclass(frozen=True)
class CurrentUser:
    id: UUID
    user_id: str
    cognito_sub: str
    login_email: str
    role: str
    status: str


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
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = verify_access_token(token)
    except CognitoJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    cognito_sub = payload["sub"]

    result = await db.execute(
        select(User).where(
            User.cognito_sub == cognito_sub,
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
        )

    if user.status.value != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active.",
        )

    return CurrentUser(
        id=user.id,
        user_id=user.user_id,
        cognito_sub=user.cognito_sub,
        login_email=user.login_email,
        role=user.role.value,
        status=user.status.value,
    )


def require_roles(*allowed_roles: str) -> Callable:
    async def dependency(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )

        return current_user

    return dependency