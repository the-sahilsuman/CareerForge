from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user
from app.api.repository_dependencies import get_db
from app.models.user import User
from app.schemas.bucket import (
    BucketCreate,
    BucketResponse,
    BucketUpdate,
)
from app.services.bucket import BucketService
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/buckets",
    tags=["Buckets"],
)


def get_bucket_service(
    db: AsyncSession = Depends(get_db),
) -> BucketService:
    return BucketService(db)


@router.get(
    "",
    response_model=list[BucketResponse],
)
async def list_buckets(
    current_user: User = Depends(get_current_user),
    service: BucketService = Depends(get_bucket_service),
):
    return await service.list_buckets(
        user_id=current_user.id,
    )


@router.get(
    "/{bucket_id}",
    response_model=BucketResponse,
)
async def get_bucket(
    bucket_id: UUID,
    current_user: User = Depends(get_current_user),
    service: BucketService = Depends(get_bucket_service),
):
    return await service.get_bucket(
        bucket_id=bucket_id,
        user_id=current_user.id,
    )


@router.post(
    "",
    response_model=BucketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_bucket(
    data: BucketCreate,
    current_user: User = Depends(get_current_user),
    service: BucketService = Depends(get_bucket_service),
):
    return await service.create_bucket(
        user_id=current_user.id,
        data=data,
    )


@router.patch(
    "/{bucket_id}",
    response_model=BucketResponse,
)
async def update_bucket(
    bucket_id: UUID,
    data: BucketUpdate,
    current_user: User = Depends(get_current_user),
    service: BucketService = Depends(get_bucket_service),
):
    return await service.update_bucket(
        bucket_id=bucket_id,
        user_id=current_user.id,
        data=data,
    )


@router.delete(
    "/{bucket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_bucket(
    bucket_id: UUID,
    current_user: User = Depends(get_current_user),
    service: BucketService = Depends(get_bucket_service),
):
    await service.delete_bucket(
        bucket_id=bucket_id,
        user_id=current_user.id,
    )

    return None