from app.schemas.event import EventOperation, EventResource, UserDataEvent


class EventRouter:
    """
    Routes Core Backend user-data events to the appropriate
    Agentic ingestion operation.

    The router does not perform ingestion itself.
    It only decides what should happen.
    """

    SUPPORTED_RESOURCES = {
        EventResource.RESUME,
        EventResource.PROFILE,
        EventResource.BIO,
        EventResource.SKILLS,
        EventResource.PROJECTS,
        EventResource.EXPERIENCE,
        EventResource.CERTIFICATIONS,
    }

    def route(self, event: UserDataEvent) -> str:
        """
        Determine the ingestion action for an event.

        Returns:
            - "upsert" for created/updated resources
            - "delete" for deleted resources

        Raises:
            ValueError: If the resource is not supported.
        """

        if event.resource not in self.SUPPORTED_RESOURCES:
            raise ValueError(
                f"Unsupported Agentic resource: {event.resource}"
            )

        if event.operation in {
            EventOperation.CREATED,
            EventOperation.UPDATED,
        }:
            return "upsert"

        if event.operation == EventOperation.DELETED:
            return "delete"

        raise ValueError(
            f"Unsupported event operation: {event.operation}"
        )