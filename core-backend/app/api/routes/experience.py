from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
)
from app.api.repository_dependencies import (
    get_experience_service,
)
from app.schemas.experience import (
    ExperienceCreate,
    ExperienceResponse,
    ExperienceUpdate,
)
from app.services.experience import ExperienceService


router = APIRouter(
    prefix="/experience",
    tags=["Experience"],
)


@router.get(
    "",
    response_model=list[ExperienceResponse],
)
async def list_experience(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ExperienceService = Depends(
        get_experience_service
    ),
):

    return await service.list_experience(
        current_user.id
    )


@router.post(
    "",
    response_model=ExperienceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_experience(
    payload: ExperienceCreate,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ExperienceService = Depends(
        get_experience_service
    ),
):

    return await service.create_experience(
        current_user.id,
        payload,
    )


@router.patch(
    "/{experience_id}",
    response_model=ExperienceResponse,
)
async def update_experience(
    experience_id: UUID,
    payload: ExperienceUpdate,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ExperienceService = Depends(
        get_experience_service
    ),
):

    return await service.update_experience(
        current_user.id,
        experience_id,
        payload,
    )


@router.delete(
    "/{experience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_experience(
    experience_id: UUID,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ExperienceService = Depends(
        get_experience_service
    ),
):

    await service.delete_experience(
        current_user.id,
        experience_id,
    )