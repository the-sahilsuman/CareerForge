from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bucket import Bucket


class BucketRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(
        self,
        user_id: UUID,
    ) -> list[Bucket]:

        result = await self.db.execute(
            select(Bucket)
            .where(
                Bucket.user_id == user_id
            )
            .order_by(
                Bucket.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        bucket_id: UUID,
        user_id: UUID,
    ) -> Bucket | None:

        result = await self.db.execute(
            select(Bucket).where(
                Bucket.id == bucket_id,
                Bucket.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        bucket: Bucket,
    ) -> Bucket:

        self.db.add(bucket)

        await self.db.flush()

        return bucket

    async def delete(
        self,
        bucket: Bucket,
    ) -> None:

        await self.db.delete(bucket)

        await self.db.flush()