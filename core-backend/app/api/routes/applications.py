from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
)
from app.api.repository_dependencies import (
    get_application_service,
)
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
)
from app.services.application import ApplicationService


router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


@router.get(
    "",
    response_model=list[ApplicationResponse],
)
async def list_applications(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ApplicationService = Depends(
        get_application_service
    ),
):

    return await service.list_applications(
        current_user.id
    )


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    payload: ApplicationCreate,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ApplicationService = Depends(
        get_application_service
    ),
):

    return await service.create_application(
        current_user.id,
        payload,
    )


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
)
async def get_application(
    application_id: UUID,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ApplicationService = Depends(
        get_application_service
    ),
):

    return await service.get_application(
        current_user.id,
        application_id,
    )


@router.patch(
    "/{application_id}",
    response_model=ApplicationResponse,
)
async def update_application(
    application_id: UUID,
    payload: ApplicationUpdate,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ApplicationService = Depends(
        get_application_service
    ),
):

    return await service.update_application(
        current_user.id,
        application_id,
        payload,
    )


@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_application(
    application_id: UUID,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ApplicationService = Depends(
        get_application_service
    ),
):

    await service.delete_application(
        current_user.id,
        application_id,
    )
