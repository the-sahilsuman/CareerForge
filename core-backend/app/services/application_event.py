from uuid import UUID

from app.models.application_event import ApplicationEvent
from app.models.enums import ApplicationStatus
from app.repositories.application_event import (
    ApplicationEventRepository,
)


class ApplicationEventService:

    def __init__(
        self,
        repository: ApplicationEventRepository,
    ):
        self.repository = repository

    async def list_events(
        self,
        application_id: UUID,
    ) -> list[ApplicationEvent]:

        return await self.repository.list_by_application(
            application_id
        )

    async def create_status_event(
        self,
        application_id: UUID,
        previous_status: ApplicationStatus | None,
        new_status: ApplicationStatus,
        source: str | None = None,
        metadata: dict | None = None,
    ) -> ApplicationEvent:

        event = ApplicationEvent(
            application_id=application_id,
            previous_status=previous_status,
            new_status=new_status,
            source=source,
            metadata_=metadata,
        )

        return await self.repository.create(event)
