from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import CurrentUser, get_current_user

from app.api.repository_dependencies import (
    get_agentic_email_service,
)
from app.schemas.agentic_email import (
    AgenticEmailResponse,
)
from app.services.agentic_email import (
    AgenticEmailService,
)


router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
)


@router.get(
    "",
    response_model=list[AgenticEmailResponse],
)
async def list_emails(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
    service: AgenticEmailService = Depends(
        get_agentic_email_service
    ),
):

    return await service.list_emails(
        current_user.id
    )

    
# @router.get(
#     "/{email_id}",
#     response_model=EmailResponse,
# )
# async def get_email(
#     email_id: UUID,
#     current_user: CurrentUser = Depends(
#         get_current_user
#     ),
#     service: EmailService = Depends(
#         get_email_service
#     ),
# ):

#     return await service.get_email(
#         current_user.id,
#         email_id,
#     )