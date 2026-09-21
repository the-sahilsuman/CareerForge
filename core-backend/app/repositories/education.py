from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.education import Education


class EducationRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(
        self,
        user_id: UUID,
    ) -> list[Education]:

        result = await self.db.execute(
            select(Education)
            .where(Education.user_id == user_id)
            .order_by(Education.start_date.desc())
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        education_id: UUID,
        user_id: UUID,
    ) -> Education | None:

        result = await self.db.execute(
            select(Education).where(
                Education.id == education_id,
                Education.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        education: Education,
    ) -> Education:

        self.db.add(education)

        await self.db.flush()

        return education

    async def delete(
        self,
        education: Education,
    ) -> None:

        await self.db.delete(education)

        await self.db.flush()