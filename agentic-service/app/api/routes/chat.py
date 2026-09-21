from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel, Field

from app.agent.models import AgentRequest
from app.agent.service import AgentService
from app.dependencies import (
    get_agent_service,
    get_internal_user_id,
)

from app.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageResponse,
)


router = APIRouter(
    prefix="/chat",
    tags=["Agent Chat"],
)


class ChatRequest(BaseModel):
    """
    Chat request received from Core Backend.

    user_id is intentionally NOT accepted from
    the browser.

    Core Backend supplies the authenticated user's
    ID through the trusted internal request headers.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )

    jd_id: str | None = Field(
        default=None,
        max_length=255,
    )


class ChatResponse(BaseModel):
    """
    Chat response returned by Agentic Service.
    """

    message: str

    user_id: str

    jd_id: str | None = None

    retrieved_chunks: int = 0

    metadata: dict = Field(
        default_factory=dict,
    )


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(
        get_internal_user_id,
    ),
    agent_service: AgentService = Depends(
        get_agent_service,
    ),
) -> ChatResponse:

    try:

        agent_request = AgentRequest(
            user_id=user_id,
            message=request.message,
            jd_id=request.jd_id,
        )

        response = await agent_service.chat(
            agent_request,
        )

        return ChatResponse(
            message=response.message,
            user_id=response.user_id,
            jd_id=response.jd_id,
            retrieved_chunks=response.retrieved_chunks,
            metadata=response.metadata,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except KeyError as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent execution failed.",
        ) from exc

@router.get(
    "/history",
    response_model=ChatHistoryResponse,
)
async def get_chat_history(
    user_id: str = Depends(
        get_internal_user_id,
    ),
) -> ChatHistoryResponse:

    from app.memory.session import session_manager

    messages = await session_manager.get_messages(
        user_id,
    )

    return ChatHistoryResponse(
        user_id=user_id,
        messages=[
            ChatMessageResponse(
                role=message.role,
                content=message.content,
                timestamp=message.timestamp,
            )
            for message in messages
            if message.role in {
                "user",
                "assistant",
            }
        ],
    )