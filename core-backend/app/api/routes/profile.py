from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user
from app.api.repository_dependencies import get_profile_service
from app.models.user import User
from app.schemas.profile import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)
from app.services.profile import ProfileService


router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


@router.get(
    "",
    response_model=ProfileResponse | None,
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    return await service.get_profile(
        current_user.id
    )


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    payload: ProfileCreate,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    return await service.create_profile(
        current_user.id,
        payload,
    )


@router.patch(
    "",
    response_model=ProfileResponse,
)
async def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    return await service.update_profile(
        current_user.id,
        payload,
    )


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_profile(
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    await service.delete_profile(
        current_user.id
    )