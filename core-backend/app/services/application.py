from datetime import datetime, timezone
from uuid import UUID

from app.core.errors import ResourceNotFoundError
from app.models.application import Application
from app.models.enums import ApplicationStatus
from app.repositories.application import ApplicationRepository
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
)


class ApplicationService:

    def __init__(
        self,
        repository: ApplicationRepository,
    ):
        self.repository = repository

    async def list_applications(
        self,
        user_id: UUID,
    ) -> list[Application]:

        return await self.repository.list_by_user(
            user_id
        )

    async def create_application(
        self,
        user_id: UUID,
        payload: ApplicationCreate,
    ) -> Application:

        application = Application(
            user_id=user_id,
            **payload.model_dump(),
        )

        if application.status == ApplicationStatus.APPLIED:
            application.applied_at = datetime.now(
                timezone.utc
            )

        return await self.repository.create(
            application
        )

    async def get_application(
        self,
        user_id: UUID,
        application_id: UUID,
    ) -> Application:

        application = await self.repository.get_by_id(
            application_id,
            user_id,
        )

        if application is None:
            raise ResourceNotFoundError(
                "Application not found."
            )

        return application

    async def update_application(
        self,
        user_id: UUID,
        application_id: UUID,
        payload: ApplicationUpdate,
    ) -> Application:

        application = await self.repository.get_by_id(
            application_id,
            user_id,
        )

        if application is None:
            raise ResourceNotFoundError(
                "Application not found."
            )

        changes = payload.model_dump(
            exclude_unset=True
        )

        new_status = changes.get("status")

        for field, value in changes.items():
            setattr(application, field, value)

        if (
            new_status == ApplicationStatus.APPLIED
            and application.applied_at is None
        ):
            application.applied_at = datetime.now(
                timezone.utc
            )

        return application

    async def delete_application(
        self,
        user_id: UUID,
        application_id: UUID,
    ) -> None:

        application = await self.repository.get_by_id(
            application_id,
            user_id,
        )

        if application is None:
            raise ResourceNotFoundError(
                "Application not found."
            )

        await self.repository.delete(application)
