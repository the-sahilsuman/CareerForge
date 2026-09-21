from uuid import UUID

from app.core.errors import ResourceNotFoundError
from app.models.certification import Certification
from app.repositories.certification import CertificationRepository
from app.schemas.certification import (
    CertificationCreate,
    CertificationUpdate,
)
from app.events.user_data import enqueue_user_data_event

class CertificationService:

    def __init__(
        self,
        repository: CertificationRepository,
    ):
        self.repository = repository

    async def list_certifications(
        self,
        user_id: UUID,
    ) -> list[Certification]:

        return await self.repository.list_by_user(
            user_id
        )

    async def create_certification(
        self,
        user_id: UUID,
        payload: CertificationCreate,
    ) -> Certification:

        certification = Certification(
            user_id=user_id,
            **payload.model_dump(),
        )

        certification = await self.repository.create(
            certification
        )

        await enqueue_user_data_event(
            self.repository.db,
            resource="certifications",
            operation="created",
            user_id=user_id,
            resource_id=certification.id,
        )

        return certification

    async def update_certification(
        self,
        user_id: UUID,
        certification_id: UUID,
        payload: CertificationUpdate,
    ) -> Certification:

        certification = await self.repository.get_by_id(
            certification_id,
            user_id,
        )

        if certification is None:
            raise ResourceNotFoundError(
                "Certification not found."
            )

        changes = payload.model_dump(
            exclude_unset=True
        )

        for field, value in changes.items():
            setattr(certification, field, value)

        await enqueue_user_data_event(
            self.repository.db,
            resource="certifications",
            operation="updated",
            user_id=user_id,
            resource_id=certification.id,
            metadata={
                "changed_fields": list(changes.keys()),
            },
        )

        return certification

    async def delete_certification(
        self,
        user_id: UUID,
        certification_id: UUID,
    ) -> None:

        certification = await self.repository.get_by_id(
            certification_id,
            user_id,
        )

        if certification is None:
            raise ResourceNotFoundError(
                "Certification not found."
            )

        await self.repository.delete(certification)

        await enqueue_user_data_event(
            self.repository.db,
            resource="certifications",
            operation="deleted",
            user_id=user_id,
            resource_id=certification_id,
        )