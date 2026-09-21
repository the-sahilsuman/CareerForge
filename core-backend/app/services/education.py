from uuid import UUID

from app.core.errors import ResourceNotFoundError
from app.models.education import Education
from app.repositories.education import EducationRepository
from app.schemas.education import (
    EducationCreate,
    EducationUpdate,
)
from app.events.user_data import enqueue_user_data_event


class EducationService:

    def __init__(
        self,
        repository: EducationRepository,
    ):
        self.repository = repository

    async def list_education(
        self,
        user_id: UUID,
    ) -> list[Education]:

        return await self.repository.list_by_user(
            user_id
        )

    async def create_education(
        self,
        user_id: UUID,
        payload: EducationCreate,
    ) -> Education:

        education = Education(
            user_id=user_id,
            **payload.model_dump(),
        )

        education = await self.repository.create(
            education
        )

        await enqueue_user_data_event(
            self.repository.db,
            resource="education",
            operation="created",
            user_id=user_id,
            resource_id=education.id,
        )

        return education


    async def update_education(
        self,
        user_id: UUID,
        education_id: UUID,
        payload: EducationUpdate,
    ) -> Education:

        education = await self.repository.get_by_id(
            education_id,
            user_id,
        )

        if education is None:
            raise ResourceNotFoundError(
                "Education record not found."
            )

        changes = payload.model_dump(
            exclude_unset=True
        )

        for field, value in changes.items():
            setattr(education, field, value)

        await enqueue_user_data_event(
            self.repository.db,
            resource="education",
            operation="updated",
            user_id=user_id,
            resource_id=education.id,
            metadata={
                "changed_fields": list(changes.keys()),
            },
        )

        return education

    async def delete_education(
        self,
        user_id: UUID,
        education_id: UUID,
    ) -> None:

        education = await self.repository.get_by_id(
            education_id,
            user_id,
        )

        if education is None:
            raise ResourceNotFoundError(
                "Education record not found."
            )

        await self.repository.delete(education)

        await enqueue_user_data_event(
            self.repository.db,
            resource="education",
            operation="deleted",
            user_id=user_id,
            resource_id=education_id,
        )