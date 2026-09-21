from uuid import UUID

from app.core.errors import ResourceNotFoundError
from app.models.experience import Experience
from app.repositories.experience import ExperienceRepository
from app.schemas.experience import (
    ExperienceCreate,
    ExperienceUpdate,
)
from app.events.user_data import enqueue_user_data_event


class ExperienceService:

    def __init__(
        self,
        repository: ExperienceRepository,
    ):
        self.repository = repository

    async def list_experience(
        self,
        user_id: UUID,
    ) -> list[Experience]:

        return await self.repository.list_by_user(
            user_id
        )

    async def create_experience(
        self,
        user_id: UUID,
        payload: ExperienceCreate,
    ) -> Experience:

        experience = Experience(
            user_id=user_id,
            **payload.model_dump(),
        )

        experience = await self.repository.create(
            experience
        )

        await enqueue_user_data_event(
            self.repository.db,
            resource="experience",
            operation="created",
            user_id=user_id,
            resource_id=experience.id,
        )

        return experience

    async def update_experience(
        self,
        user_id: UUID,
        experience_id: UUID,
        payload: ExperienceUpdate,
    ) -> Experience:

        experience = await self.repository.get_by_id(
            experience_id,
            user_id,
        )

        if experience is None:
            raise ResourceNotFoundError(
                "Experience record not found."
            )

        changes = payload.model_dump(
            exclude_unset=True
        )

        for field, value in changes.items():
            setattr(experience, field, value)

        await enqueue_user_data_event(
            self.repository.db,
            resource="experience",
            operation="updated",
            user_id=user_id,
            resource_id=experience.id,
            metadata={
                "changed_fields": list(changes.keys()),
            },
        )

        return experience

    async def delete_experience(
        self,
        user_id: UUID,
        experience_id: UUID,
    ) -> None:

        experience = await self.repository.get_by_id(
            experience_id,
            user_id,
        )

        if experience is None:
            raise ResourceNotFoundError(
                "Experience record not found."
            )

        await self.repository.delete(experience)

        await enqueue_user_data_event(
            self.repository.db,
            resource="experience",
            operation="deleted",
            user_id=user_id,
            resource_id=experience_id,
        )