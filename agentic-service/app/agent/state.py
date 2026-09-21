from typing import Any, Literal

from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """
    State used by the CareerForge LangGraph agent.

    MessagesState already provides:
        messages

    Additional fields contain information needed only during
    the current agent execution.
    """

    user_id: str

    # ---------------------------------------------------------
    # Current task
    # ---------------------------------------------------------

    task_type: Literal[
        "general_chat",
        "job_analysis",
        "email_draft",
        "email_send",
    ] | None

    # ---------------------------------------------------------
    # Current job context
    # ---------------------------------------------------------

    job_context_id: str | None

    job_description: str | None

    company_name: str | None

    job_title: str | None

    # ---------------------------------------------------------
    # Current HR/contact context
    # ---------------------------------------------------------

    hr_name: str | None

    hr_email: str | None

    # Email address CareerForge will send from.
    sender_email: str | None

    # ---------------------------------------------------------
    # Retrieved user knowledge
    # ---------------------------------------------------------

    retrieved_context: list[dict[str, Any]]

    # ---------------------------------------------------------
    # Email drafting
    # ---------------------------------------------------------

    email_subject: str | None

    email_body: str | None

    # The resume S3 key that should be attached
    # when the email is actually sent.
    resume_s3_key: str | None

    # ---------------------------------------------------------
    # Email sending
    # ---------------------------------------------------------

    email_sent: bool

    email_record_id: str | None

    # ---------------------------------------------------------
    # Errors / user-facing status
    # ---------------------------------------------------------

    error: str | None

    response: str | None