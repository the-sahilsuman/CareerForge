from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume


class ResumeRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_by_user(
        self,
        user_id: UUID,
    ) -> Resume | None:

        result = await self.db.execute(
            select(Resume).where(
                Resume.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        resume: Resume,
    ) -> Resume:

        self.db.add(resume)

        await self.db.flush()

        return resume

    async def update(
        self,
        resume: Resume,
    ) -> Resume:

        self.db.add(resume)

        await self.db.flush()

        return resume

    async def delete(
        self,
        resume: Resume,
    ) -> None:

        await self.db.delete(resume)

        await self.db.flush()