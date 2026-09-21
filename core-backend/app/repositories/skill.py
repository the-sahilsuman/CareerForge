from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill


class SkillRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(
        self,
        user_id: UUID,
    ) -> list[Skill]:

        result = await self.db.execute(
            select(Skill)
            .where(Skill.user_id == user_id)
            .order_by(Skill.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        skill_id: UUID,
        user_id: UUID,
    ) -> Skill | None:

        result = await self.db.execute(
            select(Skill).where(
                Skill.id == skill_id,
                Skill.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        skill: Skill,
    ) -> Skill:

        self.db.add(skill)

        await self.db.flush()

        return skill

    async def delete(
        self,
        skill: Skill,
    ) -> None:

        await self.db.delete(skill)

        await self.db.flush()