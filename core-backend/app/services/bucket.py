from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ResourceNotFoundError
from app.models.bucket import Bucket
from app.models.enums import BucketStatus, BucketType
from app.repositories.bucket import BucketRepository
from app.schemas.bucket import BucketCreate, BucketUpdate


class BucketService:

    def __init__(self, db: AsyncSession):
        self.repository = BucketRepository(db)

    async def list_buckets(
        self,
        user_id: UUID,
    ) -> list[Bucket]:

        return await self.repository.list_by_user(user_id)

    async def get_bucket(
        self,
        bucket_id: UUID,
        user_id: UUID,
    ) -> Bucket:

        bucket = await self.repository.get_by_id(
            bucket_id=bucket_id,
            user_id=user_id,
        )

        if bucket is None:
            raise ResourceNotFoundError(
                "Bucket not found"
            )

        return bucket

    async def create_bucket(
        self,
        user_id: UUID,
        data: BucketCreate,
    ) -> Bucket:

        bucket = Bucket(
            user_id=user_id,
            title=data.title,
            description=data.description,
            type=data.type.value,
            status=data.status.value,
        )

        return await self.repository.create(bucket)

    async def update_bucket(
        self,
        bucket_id: UUID,
        user_id: UUID,
        data: BucketUpdate,
    ) -> Bucket:

        bucket = await self.get_bucket(
            bucket_id=bucket_id,
            user_id=user_id,
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "title" in update_data:
            bucket.title = update_data["title"]

        if "description" in update_data:
            bucket.description = update_data["description"]

        if "type" in update_data:
            bucket.type = (
                update_data["type"].value
                if isinstance(update_data["type"], BucketType)
                else update_data["type"]
            )

        if "status" in update_data:
            bucket.status = (
                update_data["status"].value
                if isinstance(update_data["status"], BucketStatus)
                else update_data["status"]
            )

        return bucket

    async def delete_bucket(
        self,
        bucket_id: UUID,
        user_id: UUID,
    ) -> None:

        bucket = await self.get_bucket(
            bucket_id=bucket_id,
            user_id=user_id,
        )

        await self.repository.delete(bucket)