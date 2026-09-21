from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
)
from app.api.repository_dependencies import (
    get_education_service,
)
from app.schemas.education import (
    EducationCreate,
    EducationResponse,
    EducationUpdate,
)
from app.services.education import EducationService


router = APIRouter(
    prefix="/education",
    tags=["Education"],
)


@router.get(
    "",
    response_model=list[EducationResponse],
)
async def list_education(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: EducationService = Depends(
        get_education_service
    ),
):

    return await service.list_education(
        current_user.id
    )


@router.post(
    "",
    response_model=EducationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_education(
    payload: EducationCreate,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: EducationService = Depends(
        get_education_service
    ),
):

    return await service.create_education(
        current_user.id,
        payload,
    )


@router.patch(
    "/{education_id}",
    response_model=EducationResponse,
)
async def update_education(
    education_id: UUID,
    payload: EducationUpdate,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: EducationService = Depends(
        get_education_service
    ),
):

    return await service.update_education(
        current_user.id,
        education_id,
        payload,
    )


@router.delete(
    "/{education_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_education(
    education_id: UUID,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: EducationService = Depends(
        get_education_service
    ),
):

    await service.delete_education(
        current_user.id,
        education_id,
    )