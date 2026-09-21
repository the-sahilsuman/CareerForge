from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
)
from app.api.repository_dependencies import (
    get_certification_service,
)
from app.schemas.certification import (
    CertificationCreate,
    CertificationResponse,
    CertificationUpdate,
)
from app.services.certification import CertificationService


router = APIRouter(
    prefix="/certifications",
    tags=["Certifications"],
)


@router.get(
    "",
    response_model=list[CertificationResponse],
)
async def list_certifications(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: CertificationService = Depends(
        get_certification_service
    ),
):

    return await service.list_certifications(
        current_user.id
    )


@router.post(
    "",
    response_model=CertificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_certification(
    payload: CertificationCreate,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: CertificationService = Depends(
        get_certification_service
    ),
):

    return await service.create_certification(
        current_user.id,
        payload,
    )


@router.patch(
    "/{certification_id}",
    response_model=CertificationResponse,
)
async def update_certification(
    certification_id: UUID,
    payload: CertificationUpdate,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: CertificationService = Depends(
        get_certification_service
    ),
):

    return await service.update_certification(
        current_user.id,
        certification_id,
        payload,
    )


@router.delete(
    "/{certification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_certification(
    certification_id: UUID,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: CertificationService = Depends(
        get_certification_service
    ),
):

    await service.delete_certification(
        current_user.id,
        certification_id,
    )
    