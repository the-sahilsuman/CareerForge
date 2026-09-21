from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AgenticEmailResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    user_id: UUID
    role: str
    hr_email: str
    company_name: str
    sent_at: datetime