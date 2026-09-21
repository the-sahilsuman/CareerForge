from __future__ import annotations

from pydantic import BaseModel


class ChatMessageResponse(BaseModel):
    role: str
    content: str
    timestamp: str | None = None


class ChatHistoryResponse(BaseModel):
    user_id: str
    messages: list[ChatMessageResponse]