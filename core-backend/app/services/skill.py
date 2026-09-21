from uuid import UUID

from app.core.errors import ResourceNotFoundError
from app.models.skill import Skill
from app.repositories.skill import SkillRepository
from app.schemas.skill import SkillCreate, SkillUpdate
from app.events.user_data import enqueue_user_data_event


class SkillService:

    def __init__(
        self,
        repository: SkillRepository,
    ):
        self.repository = repository

    async def list_skills(
        self,
        user_id: UUID,
    ) -> list[Skill]:

        return await self.repository.list_by_user(
            user_id
        )

    async def create_skill(
        self,
        user_id: UUID,
        payload: SkillCreate,
    ) -> Skill:

        skill = Skill(
            user_id=user_id,
            **payload.model_dump(),
        )

        skill = await self.repository.create(
            skill
        )

        await enqueue_user_data_event(
            self.repository.db,
            resource="skills",
            operation="created",
            user_id=user_id,
            resource_id=skill.id,
        )

        return skill


    async def update_skill(
        self,
        user_id: UUID,
        skill_id: UUID,
        payload: SkillUpdate,
    ) -> Skill:

        skill = await self.repository.get_by_id(
            skill_id,
            user_id,
        )

        if skill is None:
            raise ResourceNotFoundError(
                "Skill not found."
            )

        changes = payload.model_dump(
            exclude_unset=True
        )

        for field, value in changes.items():
            setattr(skill, field, value)

        await enqueue_user_data_event(
            self.repository.db,
            resource="skills",
            operation="updated",
            user_id=user_id,
            resource_id=skill.id,
            metadata={
                "changed_fields": list(changes.keys()),
            },
        )

        return skill

    async def delete_skill(
        self,
        user_id: UUID,
        skill_id: UUID,
    ) -> None:

        skill = await self.repository.get_by_id(
            skill_id,
            user_id,
        )

        if skill is None:
            raise ResourceNotFoundError(
                "Skill not found."
            )

        await enqueue_user_data_event(
            self.repository.db,
            resource="skills",
            operation="deleted",
            user_id=user_id,
            resource_id=skill_id,
        )