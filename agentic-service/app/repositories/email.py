from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email import EmailRecord


class EmailRepository:
    """
    Repository for successful email history.

    Agentic Service owns:

        agentic.emails

    Records are created ONLY after Gmail confirms
    successful delivery acceptance.
    """

    async def create(
        self,
        *,
        session: AsyncSession,
        user_id: str,
        role: str,
        hr_email: str,
        company_name: str,
    ) -> EmailRecord:

        record = EmailRecord(
            user_id=user_id,
            role=role,
            hr_email=hr_email,
            company_name=company_name,
        )

        session.add(record)

        await session.flush()

        return record

    async def list_for_user(
        self,
        *,
        session: AsyncSession,
        user_id: str,
    ) -> list[EmailRecord]:

        result = await session.execute(
            select(EmailRecord)
            .where(
                EmailRecord.user_id == user_id
            )
            .order_by(
                desc(EmailRecord.sent_at)
            )
        )

        return list(
            result.scalars().all()
        )