from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    CurrentUser,
    get_current_user,
)
from app.api.repository_dependencies import (
    get_project_service,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.get(
    "",
    response_model=list[ProjectResponse],
)
async def list_projects(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ProjectService = Depends(
        get_project_service
    ),
):

    return await service.list_projects(
        current_user.id
    )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    payload: ProjectCreate,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ProjectService = Depends(
        get_project_service
    ),
):

    return await service.create_project(
        current_user.id,
        payload,
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ProjectService = Depends(
        get_project_service
    ),
):

    return await service.update_project(
        current_user.id,
        project_id,
        payload,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
    project_id: UUID,
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: ProjectService = Depends(
        get_project_service
    ),
):

    await service.delete_project(
        current_user.id,
        project_id,
    )
    