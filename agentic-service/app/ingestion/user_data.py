from __future__ import annotations

import asyncio
import json
from typing import Any

from app.core.logging import get_logger
from app.ingestion.models import ParsedDocument
from app.ingestion.processor import ingestion_processor
from app.repositories.user_repository import UserRepository
from app.vectorstore import s3_vector_store
from app.ingestion.service import ingestion_service


logger = get_logger(__name__)


class UserDataIngestionService:

    def __init__(self) -> None:
        self.repository = UserRepository()

    async def process_profile(
        self,
        *,
        user_id: str,
    ) -> None:

        snapshot = await self.repository.get_user_profile(
            user_id
        )

        document_id = f"profile:{user_id}"

        # User no longer exists.
        if snapshot is None:

            s3_vector_store.delete_document(
                document_id=document_id,
                user_id=user_id,
            )

            return

        # --------------------------------------------------
        # Remove previous profile vectors
        # --------------------------------------------------

        s3_vector_store.delete_document(
            document_id=document_id,
            user_id=user_id,
        )

        # --------------------------------------------------
        # Build canonical profile text
        # --------------------------------------------------

        text = self._build_profile_text(
            snapshot
        )

        if not text.strip():
            logger.warning(
                "Profile produced no text: user=%s",
                user_id,
            )
            return

        document = ParsedDocument(
            text=text,
            source_key="postgresql:careerforge",
            metadata={
                "user_id": user_id,
                "document_type": "profile",
                "source": "postgresql",
            },
        )

        ingestion_processor.process_parsed_document(
            document=document,
            user_id=user_id,
            document_id=document_id,
        )

    async def process_resume(
        self,
        *,
        user_id: str,
        operation: str,
    ) -> None:

        snapshot = await self.repository.get_user_profile(
            user_id
        )

        document_id = None

        if snapshot and snapshot.get("resume"):
            document_id = str(
                snapshot["resume"]["id"]
            )

        # Resume deleted
        if operation == "deleted":

            if document_id:
                s3_vector_store.delete_document(
                    document_id=document_id,
                    user_id=user_id,
                )

            return

        if not snapshot:
            return

        resume = snapshot.get("resume")

        if not resume:
            return

        document_id = str(
            resume["id"]
        )

        s3_key = resume.get(
            "s3_key"
        )

        if not s3_key:
            raise ValueError(
                "Resume does not contain s3_key."
            )

        # Remove old vectors before re-indexing.
        s3_vector_store.delete_document(
            document_id=document_id,
            user_id=user_id,
        )

        from app.ingestion.models import (
            IngestionMessage,
        )

        message = IngestionMessage(
            user_id=user_id,
            document_id=document_id,
            s3_key=s3_key,
            document_type="resume",
            metadata={
                "source": "resume",
                "file_name": resume.get(
                    "file_name"
                ),
            },
        )

        ingestion_service.process(
            message
        )

    @staticmethod
    def _build_profile_text(
        snapshot: dict[str, Any],
    ) -> str:

        sections: list[str] = []

        def add_section(
            title: str,
            value: Any,
        ) -> None:

            if not value:
                return

            sections.append(
                f"## {title}\n"
                f"{json.dumps(value, default=str, indent=2)}"
            )

        add_section(
            "User",
            snapshot.get("user"),
        )

        add_section(
            "Profile",
            snapshot.get("profile"),
        )

        add_section(
            "Skills",
            snapshot.get("skills"),
        )

        add_section(
            "Education",
            snapshot.get("education"),
        )

        add_section(
            "Experience",
            snapshot.get("experience"),
        )

        add_section(
            "Projects",
            snapshot.get("projects"),
        )

        add_section(
            "Certifications",
            snapshot.get("certifications"),
        )

        return "\n\n".join(sections)


user_data_ingestion_service = (
    UserDataIngestionService()
)