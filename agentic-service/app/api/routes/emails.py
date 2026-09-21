from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
)
from pydantic import BaseModel

from app.dependencies import (
    get_database_session,
    get_internal_user_id,
)
from app.repositories.email import EmailRepository


router = APIRouter(
    prefix="/emails",
    tags=["Agentic Emails"],
)


class EmailRecordResponse(BaseModel):
    id: UUID
    role: str
    hr_email: str
    company_name: str
    sent_at: datetime


email_repository = EmailRepository()


@router.get(
    "",
    response_model=list[EmailRecordResponse],
)
async def list_email_records(
    user_id: str = Depends(
        get_internal_user_id,
    ),
    session=Depends(
        get_database_session,
    ),
) -> list[EmailRecordResponse]:

    records = await email_repository.list_for_user(
        session=session,
        user_id=user_id,
    )

    return [
        EmailRecordResponse(
            id=record.id,
            role=record.role,
            hr_email=record.hr_email,
            company_name=record.company_name,
            sent_at=record.sent_at,
        )
        for record in records
    ]