from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    user_id: UUID
    title: str
    file_name: str
    s3_key: str
    object_url: str
    content_type: str
    file_size: int