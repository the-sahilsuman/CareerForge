from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
)
from app.api.repository_dependencies import (
    get_skill_service,
)
from app.schemas.skill import (
    SkillCreate,
    SkillResponse,
    SkillUpdate,
)
from app.services.skill import SkillService


router = APIRouter(
    prefix="/skills",
    tags=["Skills"],
)


@router.get(
    "",
    response_model=list[SkillResponse],
)
async def list_skills(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: SkillService = Depends(
        get_skill_service
    ),
):

    return await service.list_skills(
        current_user.id
    )


@router.post(
    "",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_skill(
    payload: SkillCreate,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: SkillService = Depends(
        get_skill_service
    ),
):

    return await service.create_skill(
        current_user.id,
        payload,
    )


@router.patch(
    "/{skill_id}",
    response_model=SkillResponse,
)
async def update_skill(
    skill_id: UUID,
    payload: SkillUpdate,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: SkillService = Depends(
        get_skill_service
    ),
):

    return await service.update_skill(
        current_user.id,
        skill_id,
        payload,
    )


@router.delete(
    "/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_skill(
    skill_id: UUID,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: SkillService = Depends(
        get_skill_service
    ),
):

    await service.delete_skill(
        current_user.id,
        skill_id,
    )