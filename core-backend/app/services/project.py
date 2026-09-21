from uuid import UUID

from app.core.errors import ResourceNotFoundError
from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)
from app.events.user_data import enqueue_user_data_event


class ProjectService:

    _URL_FIELDS = {
        "github_url",
        "live_url",
    }

    @classmethod
    def _normalize_urls(
        cls,
        data: dict,
    ) -> dict:

        for field in cls._URL_FIELDS:
            if data.get(field) is not None:
                data[field] = str(
                    data[field]
                )

        return data

    def __init__(
        self,
        repository: ProjectRepository,
    ):
        self.repository = repository

    async def list_projects(
        self,
        user_id: UUID,
    ) -> list[Project]:

        return await self.repository.list_by_user(
            user_id
        )

    async def create_project(
        self,
        user_id: UUID,
        payload: ProjectCreate,
    ) -> Project:

        project_data = self._normalize_urls(
            payload.model_dump()
        )

        project = Project(
            user_id=user_id,
            **project_data,
        )

        project = await self.repository.create(
            project
        )

        await enqueue_user_data_event(
            self.repository.db,
            resource="projects",
            operation="created",
            user_id=user_id,
            resource_id=project.id,
        )

        return project

    async def update_project(
        self,
        user_id: UUID,
        project_id: UUID,
        payload: ProjectUpdate,
    ) -> Project:

        project = await self.repository.get_by_id(
            project_id,
            user_id,
        )

        if project is None:
            raise ResourceNotFoundError(
                "Project not found."
            )

        changes = self._normalize_urls(
            payload.model_dump(
                exclude_unset=True
            )
        )

        for field, value in changes.items():
            setattr(
                project,
                field,
                value,
            )

        await enqueue_user_data_event(
            self.repository.db,
            resource="projects",
            operation="updated",
            user_id=user_id,
            resource_id=project.id,
            metadata={
                "changed_fields": list(
                    changes.keys()
                ),
            },
        )

        return project

    async def delete_project(
        self,
        user_id: UUID,
        project_id: UUID,
    ) -> None:

        project = await self.repository.get_by_id(
            project_id,
            user_id,
        )

        if project is None:
            raise ResourceNotFoundError(
                "Project not found."
            )

        await self.repository.delete(
            project
        )

        await enqueue_user_data_event(
            self.repository.db,
            resource="projects",
            operation="deleted",
            user_id=user_id,
            resource_id=project_id,
        )