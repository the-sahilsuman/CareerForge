from uuid import UUID

from fastapi import HTTPException, status

from app.api.dependencies import CurrentUser


def verify_ownership(
    resource_user_id: UUID,
    current_user: CurrentUser,
) -> None:

    if resource_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource.",
        )