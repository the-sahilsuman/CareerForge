from typing import Any

from sqlalchemy import text

from app.db import get_db_session


class UserRepository:
    """
    Read-only repository for AI ingestion.

    Uses the existing CareerForge PostgreSQL schema.
    """

    async def get_current_resume_object_url(
        self,
        user_id: str,
    ) -> str | None:

        async with get_db_session() as session:

            result = await session.execute(
                text(
                    """
                    SELECT object_url
                    FROM resumes
                    WHERE user_id = :user_id
                    LIMIT 1
                    """
                ),
                {
                    "user_id": user_id,
                },
            )

            row = result.mappings().first()

            if not row:
                return None

            object_url = row.get(
                "object_url",
            )

            if not object_url:
                return None

            return str(
                object_url,
            )


    async def get_user_profile(
        self,
        user_id: str,
    ) -> dict[str, Any] | None:

        async with get_db_session() as session:

            # -------------------------------------------------
            # User
            # -------------------------------------------------

            user_result = await session.execute(
                text(
                    """
                    SELECT
                        id,
                        user_id,
                        cognito_sub,
                        login_email,
                        role,
                        status,
                        created_at,
                        updated_at
                    FROM users
                    WHERE id = :user_id
                    """
                ),
                {
                    "user_id": user_id,
                },
            )

            user = user_result.mappings().first()

            if not user:
                return None

            # -------------------------------------------------
            # Profile
            # -------------------------------------------------

            profile_result = await session.execute(
                text(
                    """
                    SELECT *
                    FROM profiles
                    WHERE user_id = :user_id
                    """
                ),
                {
                    "user_id": user_id,
                },
            )

            profile = profile_result.mappings().first()

            # -------------------------------------------------
            # Skills
            # -------------------------------------------------

            skills_result = await session.execute(
                text(
                    """
                    SELECT *
                    FROM skills
                    WHERE user_id = :user_id
                    """
                ),
                {
                    "user_id": user_id,
                },
            )

            skills = [
                dict(row)
                for row in skills_result.mappings().all()
            ]

            # -------------------------------------------------
            # Experience
            # -------------------------------------------------

            experience_result = await session.execute(
                text(
                    """
                    SELECT *
                    FROM experience
                    WHERE user_id = :user_id
                    """
                ),
                {
                    "user_id": user_id,
                },
            )

            experience = [
                dict(row)
                for row in experience_result.mappings().all()
            ]

            # -------------------------------------------------
            # Education
            # -------------------------------------------------

            education_result = await session.execute(
                text(
                    """
                    SELECT *
                    FROM education
                    WHERE user_id = :user_id
                    """
                ),
                {
                    "user_id": user_id,
                },
            )

            education = [
                dict(row)
                for row in education_result.mappings().all()
            ]

            # -------------------------------------------------
            # Projects
            # -------------------------------------------------

            projects_result = await session.execute(
                text(
                    """
                    SELECT *
                    FROM projects
                    WHERE user_id = :user_id
                    """
                ),
                {
                    "user_id": user_id,
                },
            )

            projects = [
                dict(row)
                for row in projects_result.mappings().all()
            ]

            # -------------------------------------------------
            # Certifications
            # -------------------------------------------------

            certifications_result = await session.execute(
                text(
                    """
                    SELECT *
                    FROM certifications
                    WHERE user_id = :user_id
                    """
                ),
                {
                    "user_id": user_id,
                },
            )

            certifications = [
                dict(row)
                for row in certifications_result.mappings().all()
            ]

            # -------------------------------------------------
            # Resume
            # -------------------------------------------------

            resume_result = await session.execute(
                text(
                    """
                    SELECT
                        id,
                        s3_key,
                        object_url,
                        file_name,
                        content_type
                    FROM resumes
                    WHERE user_id = :user_id
                    LIMIT 1
                    """
                ),
                {
                    "user_id": user_id,
                },
            )

            resume = resume_result.mappings().first()

            return {
                "user": dict(user),
                "profile": (
                    dict(profile)
                    if profile
                    else {}
                ),
                "skills": skills,
                "experience": experience,
                "education": education,
                "projects": projects,
                "certifications": certifications,
                "resume": (
                    dict(resume)
                    if resume
                    else None
                ),
            }