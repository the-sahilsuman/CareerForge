from __future__ import annotations


class AgentError(Exception):
    """
    Base exception for expected agent failures.
    """

    user_message: str = (
        "I couldn't complete that request right now. "
        "Please try again."
    )

    def __init__(
        self,
        message: str | None = None,
    ) -> None:

        super().__init__(
            message or self.user_message
        )


class AgentValidationError(
    AgentError
):
    """
    Invalid user request.
    """

    user_message = (
        "Please provide a valid request."
    )


class AgentSessionError(
    AgentError
):
    """
    Conversation/session failure.
    """

    user_message = (
        "I couldn't access your conversation "
        "session right now. Please try again."
    )


class AgentRetrievalError(
    AgentError
):
    """
    Retrieval failure.
    """

    user_message = (
        "I couldn't retrieve the relevant "
        "profile or job information right now."
    )


class AgentLLMError(
    AgentError
):
    """
    LLM/provider failure.
    """

    user_message = (
        "I'm unable to generate a response right now. "
        "Please try again in a moment."
    )


class AgentEmailError(
    AgentError
):
    """
    Email workflow failure.
    """

    user_message = (
        "I couldn't complete the email request right now."
    )