from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.experience import Experience


class ExperienceRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(
        self,
        user_id: UUID,
    ) -> list[Experience]:

        result = await self.db.execute(
            select(Experience)
            .where(Experience.user_id == user_id)
            .order_by(Experience.start_date.desc())
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        experience_id: UUID,
        user_id: UUID,
    ) -> Experience | None:

        result = await self.db.execute(
            select(Experience).where(
                Experience.id == experience_id,
                Experience.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        experience: Experience,
    ) -> Experience:

        self.db.add(experience)

        await self.db.flush()

        return experience

    async def delete(
        self,
        experience: Experience,
    ) -> None:

        await self.db.delete(experience)

        await self.db.flush()