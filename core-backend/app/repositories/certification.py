from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certification import Certification


class CertificationRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(
        self,
        user_id: UUID,
    ) -> list[Certification]:

        result = await self.db.execute(
            select(Certification)
            .where(Certification.user_id == user_id)
            .order_by(Certification.issue_date.desc())
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        certification_id: UUID,
        user_id: UUID,
    ) -> Certification | None:

        result = await self.db.execute(
            select(Certification).where(
                Certification.id == certification_id,
                Certification.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        certification: Certification,
    ) -> Certification:

        self.db.add(certification)

        await self.db.flush()

        return certification

    async def delete(
        self,
        certification: Certification,
    ) -> None:

        await self.db.delete(certification)

        await self.db.flush()