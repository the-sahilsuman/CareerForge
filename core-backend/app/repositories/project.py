from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(
        self,
        user_id: UUID,
    ) -> list[Project]:

        result = await self.db.execute(
            select(Project)
            .where(Project.user_id == user_id)
            .order_by(Project.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> Project | None:

        result = await self.db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        project: Project,
    ) -> Project:

        self.db.add(project)

        await self.db.flush()

        return project

    async def delete(
        self,
        project: Project,
    ) -> None:

        await self.db.delete(project)

        await self.db.flush()