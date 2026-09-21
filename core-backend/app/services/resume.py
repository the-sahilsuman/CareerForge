from uuid import UUID

from app.clients.s3 import S3Client
from app.core.errors import ResourceNotFoundError
from app.models.resume import Resume
from app.repositories.resume import ResumeRepository
from app.services.outbox import OutboxService


class ResumeService:

    def __init__(
        self,
        repository: ResumeRepository,
        s3_client: S3Client,
    ):
        self.repository = repository
        self.s3_client = s3_client

    async def upload_resume(
        self,
        user_id: UUID,
        *,
        file_bytes: bytes,
        file_name: str,
        content_type: str,
    ) -> Resume:

        resume = await self.repository.get_by_user(
            user_id
        )

        is_new_resume = resume is None

        s3_key = (
            f"users/{user_id}/resumes/{file_name}"
        )

        self.s3_client.upload_file(
            file_bytes=file_bytes,
            key=s3_key,
            content_type=content_type,
        )

        object_url = self.s3_client.get_object_url(
            key=s3_key
        )

        if resume is None:

            resume = Resume(
                user_id=user_id,
                title=file_name,
                file_name=file_name,
                s3_key=s3_key,
                object_url=object_url,
                content_type=content_type,
                file_size=len(file_bytes),
            )

            await self.repository.create(
                resume
            )

        else:

            old_s3_key = resume.s3_key

            resume.title = file_name
            resume.file_name = file_name
            resume.s3_key = s3_key
            resume.object_url = object_url
            resume.content_type = content_type
            resume.file_size = len(file_bytes)

            await self.repository.update(
                resume
            )

            if old_s3_key != s3_key:
                self.s3_client.delete_object(
                    key=old_s3_key
                )

        # ------------------------------------------
        # Create ingestion event
        # ------------------------------------------

        outbox = OutboxService(
            self.repository.db
        )

        await outbox.enqueue(
            event_type=(
                "resume.created"
                if is_new_resume
                else "resume.updated"
            ),
            aggregate_type="resume",
            aggregate_id=resume.id,
            payload={
                "user_id": str(user_id),
                "resource": "resume",
                "operation": (
                    "created"
                    if is_new_resume
                    else "updated"
                ),
                "resource_id": str(resume.id),
                "s3_key": resume.s3_key,
                "file_name": resume.file_name,
                "content_type": resume.content_type,
            },
        )

        return resume

    async def get_resume(
        self,
        user_id: UUID,
    ) -> Resume | None:

        return await self.repository.get_by_user(
            user_id
        )

    async def delete_resume(
        self,
        user_id: UUID,
    ) -> None:

        resume = await self.repository.get_by_user(
            user_id
        )

        if resume is None:
            return

        resume_id = resume.id

        self.s3_client.delete_object(
            key=resume.s3_key
        )

        await self.repository.delete(
            resume
        )

        # ------------------------------------------
        # Create deletion event
        # ------------------------------------------

        outbox = OutboxService(
            self.repository.db
        )

        await outbox.enqueue(
            event_type="resume.deleted",
            aggregate_type="resume",
            aggregate_id=resume_id,
            payload={
                "user_id": str(user_id),
                "resource": "resume",
                "operation": "deleted",
                "resource_id": str(resume_id),
            },
        )

    async def get_download_url(
        self,
        user_id: UUID,
    ) -> dict[str, str]:

        resume = await self.repository.get_by_user(
            user_id
        )

        if resume is None:
            raise ResourceNotFoundError(
                "Resume not found."
            )

        download_url = (
            self.s3_client.generate_download_url(
                key=resume.s3_key,
                expires_in=3600,
            )
        )

        return {
            "download_url": download_url
        }