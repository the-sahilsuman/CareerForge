from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
)
from app.api.repository_dependencies import (
    get_cognito_client,
    get_user_service,
)
from app.clients.cognito import (
    CognitoClient,
    CognitoClientError,
)
from app.schemas.user import ProvisionUserRequest
from app.services.user import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "/provision",
    status_code=status.HTTP_200_OK,
)
async def provision_user(
    payload: ProvisionUserRequest,
    service: UserService = Depends(
        get_user_service
    ),
    cognito: CognitoClient = Depends(
        get_cognito_client
    ),
):
    """
    Provision a Cognito-confirmed user into
    the CareerForge PostgreSQL database.

    This endpoint is intentionally unauthenticated.

    Reason:
    The user has just completed Cognito email
    verification and therefore may not have an
    access token yet.

    Cognito is used as the source of truth.
    """

    username = payload.username.strip()

    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cognito username is required.",
        )

    try:
        cognito_user = cognito.get_confirmed_user(
            username=username,
        )

    except CognitoClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    cognito_sub = cognito.get_attribute(
        cognito_user,
        "sub",
    )

    if not cognito_sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cognito user does not contain "
                "a sub attribute."
            ),
        )

    login_email = cognito.get_attribute(
        cognito_user,
        "email",
    )

    if not login_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cognito user does not contain "
                "an email attribute."
            ),
        )

    email_verified = cognito.get_attribute(
        cognito_user,
        "email_verified",
    )

    if email_verified != "true":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cognito email is not marked "
                "as verified."
            ),
        )

    try:
        user = await service.get_or_create_from_cognito(
            cognito_sub=cognito_sub,
            login_email=login_email,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Cognito user was verified, but "
                "CareerForge database provisioning failed."
            ),
        ) from exc

    return {
        "data": {
            "id": str(user.id),
            "user_id": user.user_id,
            "cognito_sub": user.cognito_sub,
            "login_email": user.login_email,
            "role": user.role,
            "status": user.status,
        }
    }


@router.post(
    "/me",
    status_code=status.HTTP_200_OK,
)
async def bootstrap_current_user(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: UserService = Depends(
        get_user_service
    ),
):
    """
    Return the current CareerForge user.

    The user should already have been provisioned
    immediately after Cognito confirmation.
    """

    user = await service.get_or_create_from_cognito(
        cognito_sub=current_user.cognito_sub,
        login_email=current_user.login_email,
    )

    return {
        "data": {
            "id": str(user.id),
            "user_id": user.user_id,
            "cognito_sub": user.cognito_sub,
            "login_email": user.login_email,
            "role": user.role,
            "status": user.status,
        }
    }