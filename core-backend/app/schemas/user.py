from pydantic import BaseModel, Field

class ProvisionUserRequest(BaseModel):
    username: str = Field(
    min_length=1,
    max_length=255,
    )

class UserResponse(BaseModel):
    id: str
    user_id: str
    cognito_sub: str
    login_email: str
    role: str
    status: str
