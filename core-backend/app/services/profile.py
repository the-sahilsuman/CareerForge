from uuid import UUID

from app.core.errors import (
    ConflictError,
    ResourceNotFoundError,
)
from app.models.profile import Profile
from app.repositories.email_connection import (
    EmailConnectionRepository,
)
from app.repositories.profile import ProfileRepository
from app.schemas.profile import (
    ProfileCreate,
    ProfileUpdate,
)
from app.events.user_data import enqueue_user_data_event

class ProfileService:

    def __init__(
        self,
        repository: ProfileRepository,
        email_connection_repository: EmailConnectionRepository,
    ):
        self.repository = repository
        self.email_connection_repository = (
            email_connection_repository
        )

    async def get_profile(
        self,
        user_id: UUID,
    ) -> Profile:

        profile = await self.repository.get_by_user_id(
            user_id
        )

        if profile is None:
            raise ResourceNotFoundError(
                "Profile not found."
            )

        return profile

    async def create_profile(
        self,
        user_id: UUID,
        payload: ProfileCreate,
    ) -> Profile:

        existing = await self.repository.get_by_user_id(
            user_id
        )

        if existing:
            raise ConflictError(
                "Profile already exists."
            )

        profile_data = payload.model_dump()

        for field in (
            "linkedin_url",
            "github_url",
            "portfolio_url",
        ):
            if profile_data.get(field) is not None:
                profile_data[field] = str(
                    profile_data[field]
                )

        if profile_data.get("professional_email"):
            profile_data["professional_email"] = str(
                profile_data["professional_email"]
            )

        profile = Profile(
            user_id=user_id,
            **profile_data,
        )

        profile = await self.repository.create(
            profile
        )

        await enqueue_user_data_event(
            self.repository.db,
            resource="profile",
            operation="created",
            user_id=user_id,
            resource_id=profile.id,
        )

        return profile


    async def update_profile(
        self,
        user_id: UUID,
        payload: ProfileUpdate,
    ) -> Profile:

        profile = await self.repository.get_by_user_id(
            user_id
        )

        if profile is None:
            raise ResourceNotFoundError(
                "Profile not found."
            )

        changes = payload.model_dump(
            exclude_unset=True
        )

        if "professional_email" in changes:

            new_email = changes.pop(
                "professional_email"
            )

            if new_email is not None:
                new_email = str(new_email)

            current_email = profile.professional_email

            current_normalized = (
                current_email.strip().lower()
                if current_email
                else None
            )

            new_normalized = (
                new_email.strip().lower()
                if new_email
                else None
            )

            if current_normalized != new_normalized:

                # --------------------------------------------------
                # Professional email changed.
                #
                # The existing Gmail connection can no longer be
                # trusted for the new professional email.
                #
                # Delete the connection completely.
                # --------------------------------------------------

                existing_connection = (
                    await self.email_connection_repository
                    .get_by_user_id(user_id)
                )

                if existing_connection:
                    await self.email_connection_repository.delete(
                        existing_connection
                    )

                profile.professional_email = (
                    new_email
                )

        url_fields = {
            "linkedin_url",
            "github_url",
            "portfolio_url",
        }

        for field, value in changes.items():

            if field in url_fields and value is not None:
                value = str(value)

            setattr(
                profile,
                field,
                value,
            )

        profile = await self.repository.update(
            profile
        )

        await enqueue_user_data_event(
            self.repository.db,
            resource="profile",
            operation="updated",
            user_id=user_id,
            resource_id=profile.id,
            metadata={
                "changed_fields": list(changes.keys()),
            },
        )

        return profile

    async def delete_profile(
        self,
        user_id: UUID,
    ) -> None:

        profile = await self.repository.get_by_user_id(
            user_id
        )

        if profile is None:
            raise ResourceNotFoundError(
                "Profile not found."
            )

        await enqueue_user_data_event(
            self.repository.db,
            resource="profile",
            operation="deleted",
            user_id=user_id,
            resource_id=profile.id,
        )