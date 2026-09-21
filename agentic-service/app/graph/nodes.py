from __future__ import annotations

import re
from typing import Any

from app.agent.context import context_builder
from app.agent.llm import get_llm_provider
from app.agent.prompts import (
    SYSTEM_PROMPT,
    build_agent_prompt,
)
from app.core.logging import get_logger
from app.graph.state import AgentGraphState
from app.jd.analyzer import JDAnalyzer
from app.jd.matcher import JDMatcher
from app.memory import session_manager
from app.memory.models import (
    ChatSession,
    JDContext,
)
from app.retrieval import retrieval_service
from app.routing import (
    Intent,
    routing_service,
)

from app.email.connection import (
    EmailConnectionError,
    EmailCredentialsError,
    EmailNotConnectedError,
    email_connection_service,
)

from app.email.drafting import (
    EmailDraft,
    EmailDraftingService,
)

from app.db import get_db_session

from app.email.execution import (
    EmailExecutionError,
    GmailEmailExecutor,
)

from app.jd.extractor import jd_extractor

from app.repositories.email import EmailRepository
from app.repositories.user_repository import UserRepository


logger = get_logger(__name__)


# ============================================================
# Services
# ============================================================

llm = get_llm_provider()

email_drafting_service = EmailDraftingService(
    llm=llm,
)

jd_analyzer = JDAnalyzer(
    llm=llm,
)

jd_matcher = JDMatcher()

email_executor = GmailEmailExecutor()

email_repository = EmailRepository()

user_repository = UserRepository()


# ============================================================
# Load Session
# ============================================================


async def load_session(
    state: AgentGraphState,
) -> dict[str, Any]:

    user_id = state["user_id"]

    session = await session_manager.get_or_create(
        user_id,
    )

    logger.debug(
        "Loaded session: user=%s active_jd=%s",
        user_id,
        session.active_jd_id,
    )

    return {
        "session": session,
    }


# ============================================================
# JD Detection + Storage
# ============================================================


async def detect_and_store_jd(
    state: AgentGraphState,
) -> dict[str, Any]:

    message = state["message"]

    extraction = await jd_extractor.extract(
        message,
    )

    if not extraction.is_job_description:

        logger.debug(
            "No new JD detected: user=%s",
            state["user_id"],
        )

        return {}

    if not extraction.jd_id:

        raise ValueError(
            "JD was detected but no internal JD ID was created."
        )

    session = await session_manager.add_jd(
        user_id=state["user_id"],
        jd_id=extraction.jd_id,
        title=extraction.title,
        company=extraction.company,
        description=extraction.description,
        metadata={
            "source": "user_message",
            "detection_confidence": (
                extraction.confidence
            ),
        },
    )

    logger.info(
        "New JD detected and stored: "
        "user=%s jd=%s company=%s title=%s",
        state["user_id"],
        extraction.jd_id,
        extraction.company,
        extraction.title,
    )

    return {
        "session": session,
        "detected_jd_id": extraction.jd_id,
        "detected_jd_title": extraction.title,
        "detected_jd_company": extraction.company,
        "detected_jd_confidence": (
            extraction.confidence
        ),
    }


# ============================================================
# Route Request
# ============================================================


async def route_request(
    state: AgentGraphState,
) -> dict[str, Any]:

    message = state["message"]

    session = state["session"]

    available_jds = [
        {
            "jd_id": jd.jd_id,
            "title": jd.title,
            "company": jd.company,
        }
        for jd in session.jd_contexts.values()
    ]

    result = await routing_service.route(
        message=message,
        active_jd_id=session.active_jd_id,
        available_jds=available_jds,
    )

    logger.info(
        "Agent route: user=%s intent=%s confidence=%.3f jd=%s",
        state["user_id"],
        result.intent,
        result.confidence,
        result.jd_id,
    )

    return {
        "route_result": result,
    }


# ============================================================
# JD Resolution
# ============================================================


async def resolve_jd(
    state: AgentGraphState,
) -> dict[str, Any]:

    request_jd_id = state.get(
        "jd_id",
    )

    message = state["message"]

    session = state["session"]

    route_result = state["route_result"]

    resolved_jd = _resolve_jd(
        request_jd_id=request_jd_id,
        message=message,
        session=session,
        route_intent=route_result.intent,
        routed_jd_id=route_result.jd_id,
    )

    if (
        resolved_jd is not None
        and session.active_jd_id
        != resolved_jd.jd_id
    ):

        await session_manager.set_active_jd(
            user_id=state["user_id"],
            jd_id=resolved_jd.jd_id,
        )

        session = await session_manager.get_session(
            state["user_id"],
        )

    active_jd = await session_manager.get_active_jd(
        state["user_id"],
    )

    logger.info(
        "Resolved active JD: user=%s jd=%s",
        state["user_id"],
        active_jd.jd_id
        if active_jd
        else None,
    )

    return {
        "session": session,
        "active_jd": active_jd,
    }


def _resolve_jd(
    *,
    request_jd_id: str | None,
    message: str,
    session: ChatSession,
    route_intent: Intent,
    routed_jd_id: str | None,
) -> JDContext | None:

    # --------------------------------------------------------
    # Explicit JD
    # --------------------------------------------------------

    if request_jd_id:

        jd = session.jd_contexts.get(
            request_jd_id,
        )

        if jd is None:

            raise KeyError(
                f"JD not found in session: "
                f"{request_jd_id}"
            )

        return jd

    # --------------------------------------------------------
    # Router JD
    # --------------------------------------------------------

    if routed_jd_id:

        jd = session.jd_contexts.get(
            routed_jd_id,
        )

        if jd is not None:

            return jd

    # --------------------------------------------------------
    # Natural reference
    # --------------------------------------------------------

    reference = _extract_jd_reference(
        message=message,
        session=session,
    )

    if reference:

        jd = session_manager.resolve_jd_reference(
            session,
            reference,
        )

        if jd is not None:

            return jd

    # --------------------------------------------------------
    # Relative reference
    # --------------------------------------------------------

    relative_jd = _resolve_relative_jd(
        message=message,
        session=session,
    )

    if relative_jd is not None:

        return relative_jd

    # --------------------------------------------------------
    # Single JD
    # --------------------------------------------------------

    if (
        len(session.jd_contexts) == 1
        and route_intent in {
            Intent.JD_ANALYSIS,
            Intent.JD_MATCH,
            Intent.JD_SWITCH,
            Intent.EMAIL_DRAFT,
            Intent.EMAIL_SEND,
        }
    ):

        return next(
            iter(
                session.jd_contexts.values()
            )
        )

    # --------------------------------------------------------
    # Current active JD
    # --------------------------------------------------------

    if session.active_jd_id:

        return session.jd_contexts.get(
            session.active_jd_id,
        )

    return None


def _extract_jd_reference(
    *,
    message: str,
    session: ChatSession,
) -> str | None:

    if not message.strip():

        return None

    normalised_message = (
        " ".join(
            message.lower()
            .strip()
            .split()
        )
    )

    matches: list[str] = []

    for jd_id, jd in session.jd_contexts.items():

        candidates = [
            jd_id,
            jd.title,
            jd.company,
        ]

        for candidate in candidates:

            if not candidate:

                continue

            candidate_normalised = (
                " ".join(
                    candidate.lower()
                    .strip()
                    .split()
                )
            )

            if not candidate_normalised:

                continue

            pattern = (
                r"(?<!\w)"
                + re.escape(
                    candidate_normalised,
                )
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                normalised_message,
            ):

                matches.append(
                    jd_id,
                )

                break

    unique_matches = list(
        dict.fromkeys(matches)
    )

    if len(unique_matches) == 1:

        return unique_matches[0]

    return None


def _resolve_relative_jd(
    *,
    message: str,
    session: ChatSession,
) -> JDContext | None:

    if not session.active_jd_id:

        return None

    normalised = message.lower()

    patterns = [
        r"\bthe other job\b",
        r"\bthe other role\b",
        r"\banother job\b",
        r"\banother role\b",
        r"\bthe other company\b",
        r"\bthe other jd\b",
        r"\bswitch to the other\b",
        r"\bgo to the other\b",
    ]

    if not any(
        re.search(
            pattern,
            normalised,
        )
        for pattern in patterns
    ):

        return None

    alternatives = [
        jd
        for jd_id, jd in session.jd_contexts.items()
        if jd_id != session.active_jd_id
    ]

    if len(alternatives) == 1:

        return alternatives[0]

    return None


# ============================================================
# Retrieval
# ============================================================


async def retrieve_context(
    state: AgentGraphState,
) -> dict[str, Any]:

    user_id = state["user_id"]

    message = state["message"]

    active_jd = state.get(
        "active_jd",
    )

    document_id = None

    if active_jd:

        document_id = active_jd.metadata.get(
            "document_id",
        )

    chunks = await retrieval_service.search_text(
        user_id=user_id,
        query=message,
        top_k=5,
        document_id=document_id,
    )

    logger.info(
        "Retrieved %d chunks for user=%s",
        len(chunks),
        user_id,
    )

    return {
        "retrieved_chunks": chunks,
    }


# ============================================================
# JD Intelligence
# ============================================================


async def analyze_jd(
    state: AgentGraphState,
) -> dict[str, Any]:

    active_jd = state.get(
        "active_jd",
    )

    route_result = state["route_result"]

    if active_jd is None:

        return {
            "jd_analysis": None,
            "jd_match": None,
        }

    if route_result.intent not in {
        Intent.JD_ANALYSIS,
        Intent.JD_MATCH,
    }:

        return {
            "jd_analysis": None,
            "jd_match": None,
        }

    analysis = await jd_analyzer.analyze(
        active_jd,
    )

    match = jd_matcher.match(
        analysis=analysis,
        chunks=state.get(
            "retrieved_chunks",
            [],
        ),
    )

    logger.info(
        "JD intelligence completed: "
        "jd=%s matched=%d missing=%d",
        active_jd.jd_id,
        len(match.matched_skills),
        len(match.missing_required_skills),
    )

    return {
        "jd_analysis": analysis,
        "jd_match": match,
    }


# ============================================================
# Build Context
# ============================================================


def build_context(
    state: AgentGraphState,
) -> dict[str, str]:

    session = state["session"]

    active_jd = state.get(
        "active_jd",
    )

    chunks = state.get(
        "retrieved_chunks",
        [],
    )

    base_context = context_builder.build(
        request=_build_request(state),
        messages=session.messages,
        session=session,
        active_jd=active_jd,
        chunks=chunks,
    )

    intelligence_context = (
        _build_jd_intelligence_context(
            state,
        )
    )

    return {
        "conversation_context": base_context[
            "conversation"
        ],
        "session_jds_context": base_context[
            "session_jds"
        ],
        "jd_context": base_context[
            "active_jd"
        ],
        "retrieved_context": base_context[
            "retrieved_context"
        ],
        "jd_intelligence_context": (
            intelligence_context
        ),
    }


def _build_request(
    state: AgentGraphState,
):
    """
    Construct the existing AgentRequest object expected
    by ContextBuilder.
    """

    from app.agent.models import AgentRequest

    return AgentRequest(
        user_id=state["user_id"],
        message=state["message"],
        jd_id=state.get("jd_id"),
    )


def _build_jd_intelligence_context(
    state: AgentGraphState,
) -> str:

    analysis = state.get(
        "jd_analysis",
    )

    match = state.get(
        "jd_match",
    )

    if analysis is None:

        return ""

    sections: list[str] = []

    if analysis.summary:

        sections.append(
            "JD SUMMARY:\n"
            + analysis.summary
        )

    if analysis.required_skills:

        sections.append(
            "REQUIRED SKILLS:\n"
            + "\n".join(
                f"- {skill}"
                for skill in analysis.required_skills
            )
        )

    if analysis.preferred_skills:

        sections.append(
            "PREFERRED SKILLS:\n"
            + "\n".join(
                f"- {skill}"
                for skill in analysis.preferred_skills
            )
        )

    if analysis.responsibilities:

        sections.append(
            "RESPONSIBILITIES:\n"
            + "\n".join(
                f"- {item}"
                for item in analysis.responsibilities
            )
        )

    if analysis.experience_requirements:

        sections.append(
            "EXPERIENCE REQUIREMENTS:\n"
            + "\n".join(
                f"- {item}"
                for item in analysis.experience_requirements
            )
        )

    if analysis.education_requirements:

        sections.append(
            "EDUCATION REQUIREMENTS:\n"
            + "\n".join(
                f"- {item}"
                for item in analysis.education_requirements
            )
        )

    if analysis.keywords:

        sections.append(
            "JD KEYWORDS:\n"
            + ", ".join(
                analysis.keywords,
            )
        )

    if match is not None:

        match_text = match.as_text()

        if match_text:

            sections.append(
                "JD / USER MATCH ANALYSIS:\n"
                + match_text
            )

    return "\n\n".join(
        sections,
    )


# ============================================================
# Email Drafting
# ============================================================


def _extract_recipient_email(
    message: str,
) -> str | None:
    """
    Extract the recipient email address from the user's
    message.

    Example:

        send email to HR: hr@example.com

    returns:

        hr@example.com
    """

    if not message:

        return None

    match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        message,
    )

    if not match:

        return None

    return match.group(0).strip()


async def draft_email(
    state: AgentGraphState,
) -> dict[str, Any]:
    """
    Generate a personalised application email for the
    currently active JD.

    This node is responsible for:
        - validating the active JD
        - validating retrieved profile context
        - extracting the recipient email
        - calling EmailDraftingService with its actual interface
        - ensuring the extracted recipient is preserved

    This node does NOT:
        - send the email
        - create an email history record
        - modify the Gmail connection
    """

    # --------------------------------------------------------
    # Active JD
    # --------------------------------------------------------

    active_jd = state.get(
        "active_jd",
    )

    if active_jd is None:

        raise RuntimeError(
            "Cannot draft an email without an active JD."
        )

    # --------------------------------------------------------
    # Retrieved profile / resume context
    #
    # build_context() has already converted the retrieved
    # chunks into a string stored in retrieved_context.
    # --------------------------------------------------------

    profile_context = state.get(
        "retrieved_context",
        "",
    )

    if not profile_context:

        raise RuntimeError(
            "Cannot draft an email without profile context."
        )

    # --------------------------------------------------------
    # Extract recipient email from the current user message.
    # --------------------------------------------------------

    recipient_email = _extract_recipient_email(
        state["message"],
    )

    # Fall back to state if another node has supplied it.

    if not recipient_email:

        recipient_email = state.get(
            "recipient_email",
        )

    if not recipient_email:

        raise RuntimeError(
            "Cannot draft an email without a recipient email."
        )

    # --------------------------------------------------------
    # Build the JD context.
    #
    # EmailDraftingService expects active_jd as a STRING,
    # not a JDContext object.
    #
    # build_context() already creates the correct formatted
    # representation and stores it as jd_context.
    # --------------------------------------------------------

    jd_context = state.get(
        "jd_context",
        "",
    )

    if not jd_context:

        raise RuntimeError(
            "Cannot draft an email without JD context."
        )

    # --------------------------------------------------------
    # Conversation context
    # --------------------------------------------------------

    conversation_context = state.get(
        "conversation_context",
        "",
    )

    # --------------------------------------------------------
    # JD intelligence context
    #
    # This may be empty for EMAIL_SEND / EMAIL_DRAFT because
    # JD intelligence is only generated for JD_ANALYSIS and
    # JD_MATCH.
    #
    # EmailDraftingService accepts an optional empty value.
    # --------------------------------------------------------

    jd_intelligence_context = state.get(
        "jd_intelligence_context",
        "",
    )

    # --------------------------------------------------------
    # Generate personalised email.
    #
    # IMPORTANT:
    #
    # This matches the actual EmailDraftingService.draft()
    # signature:
    #
    #     user_message
    #     active_jd
    #     retrieved_context
    #     conversation
    #     jd_intelligence
    # --------------------------------------------------------

    draft = await email_drafting_service.draft(
        user_message=state["message"],
        active_jd=jd_context,
        retrieved_context=profile_context,
        conversation=conversation_context,
        jd_intelligence=jd_intelligence_context,
    )

    # --------------------------------------------------------
    # Preserve the recipient extracted from the user's
    # explicit request.
    #
    # Example:
    #
    # "send email for google, hr:
    #  apexsahilsuman@gmail.com"
    #
    # The node already knows the exact recipient.
    # Do not depend on the LLM to reproduce it correctly.
    # --------------------------------------------------------

    draft.recipient_email = recipient_email

    logger.info(
        "Email draft generated: "
        "user=%s jd=%s recipient=%s",
        state["user_id"],
        active_jd.jd_id,
        recipient_email,
    )

    return {
        "email_draft": draft,
        "recipient_email": recipient_email,
    }

# ============================================================
# Send Email
# ============================================================


async def send_email(
    state: AgentGraphState,
) -> dict[str, Any]:

    route_result = state["route_result"]

    if route_result.intent != Intent.EMAIL_SEND:

        return {
            "email_send_result": None,
            "email_record_id": None,
        }

    # --------------------------------------------------------
    # Email draft must exist.
    # --------------------------------------------------------

    draft = state.get(
        "email_draft",
    )

    if draft is None:

        raise RuntimeError(
            "Cannot send email because no email draft exists."
        )

    logger.info(
        "Sending email: "
        "user=%s recipient=%s subject=%s",
        state["user_id"],
        draft.recipient_email,
        draft.subject,
    )

    # --------------------------------------------------------
    # Gmail credentials.
    # --------------------------------------------------------

    credentials = state.get(
        "email_credentials",
    )

    if credentials is None:

        raise RuntimeError(
            "Cannot send email without Gmail credentials."
        )

    user_id = state["user_id"]

    # --------------------------------------------------------
    # Get current resume.
    #
    # Read-only access to Core-owned resume data.
    # --------------------------------------------------------

    resume_s3_url = (
        await user_repository.get_current_resume_object_url(
            user_id,
        )
    )

    if not resume_s3_url:

        raise EmailExecutionError(
            "No current resume is available for the email."
        )

    # --------------------------------------------------------
    # SEND EMAIL FIRST.
    #
    # No agentic.emails record is created before Gmail
    # succeeds.
    # --------------------------------------------------------

    result = await email_executor.send(
        draft=draft,
        credentials=credentials,
        resume_s3_url=resume_s3_url,
    )

    # --------------------------------------------------------
    # Gmail succeeded.
    #
    # Now create successful email history in:
    #
    #     agentic.emails
    #
    # We store metadata only, not the full email body.
    # --------------------------------------------------------

    active_jd = state.get(
        "active_jd",
    )

    role = (
        active_jd.title
        if active_jd is not None
        and active_jd.title
        else "Not specified"
    )

    company_name = (
        active_jd.company
        if active_jd is not None
        and active_jd.company
        else "Not specified"
    )

    hr_email = (
        draft.recipient_email
        or ""
    ).strip()

    if not hr_email:

        raise EmailExecutionError(
            "Email was sent but recipient information "
            "was unavailable for recording."
        )

    async with get_db_session() as session:

        record = await email_repository.create(
            session=session,
            user_id=user_id,
            role=role,
            hr_email=hr_email,
            company_name=company_name,
        )

        record_id = str(
            record.id,
        )

    logger.info(
        "Successful email recorded in agentic.emails: "
        "user=%s record_id=%s role=%s company=%s hr=%s",
        user_id,
        record_id,
        role,
        company_name,
        hr_email,
    )

    return {
        "email_send_result": result,
        "email_record_id": record_id,
        "resume_s3_url": resume_s3_url,
    }


# ============================================================
# Generate Response
# ============================================================


async def generate_response(
    state: AgentGraphState,
) -> dict[str, str]:

    route_result = state["route_result"]

    # ========================================================
    # Email Draft
    # ========================================================

    if route_result.intent == Intent.EMAIL_DRAFT:

        draft = state.get(
            "email_draft",
        )

        if draft is None:

            raise RuntimeError(
                "Email draft was not generated.",
            )

        return {
            "answer": _format_email_draft(
                draft,
            ),
        }

    # ========================================================
    # Email Send
    # ========================================================

    if route_result.intent == Intent.EMAIL_SEND:

        draft = state.get(
            "email_draft",
        )

        send_result = state.get(
            "email_send_result",
        )

        if draft is None:

            raise RuntimeError(
                "Email draft was not generated."
            )

        if send_result is None:

            raise RuntimeError(
                "Email was not sent."
            )

        return {
            "answer": (
                "Email sent successfully to "
                f"{draft.recipient_email}."
            ),
        }

    # ========================================================
    # Normal Agent Response
    # ========================================================

    prompt = build_agent_prompt(
        user_message=state["message"],
        conversation=state.get(
            "conversation_context",
            "",
        ),
        active_jd=state.get(
            "jd_context",
            "",
        ),
        session_jds=state.get(
            "session_jds_context",
            "",
        ),
        retrieved_context=state.get(
            "retrieved_context",
            "",
        ),
        jd_intelligence=state.get(
            "jd_intelligence_context",
            "",
        ),
    )

    answer = await llm.generate(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt,
    )

    if not answer:

        raise RuntimeError(
            "LLM returned an empty response.",
        )

    return {
        "answer": answer.strip(),
    }


def _format_email_draft(
    draft: EmailDraft,
) -> str:
    """
    Convert the structured email draft into the
    user-facing response.

    This is presentation only.
    """

    lines: list[str] = []

    lines.append(
        "Here is the drafted email:"
    )

    lines.append("")

    if draft.recipient_email:

        if draft.recipient_name:

            lines.append(
                f"To: {draft.recipient_name} "
                f"<{draft.recipient_email}>"
            )

        else:

            lines.append(
                f"To: {draft.recipient_email}"
            )

    elif draft.recipient_name:

        lines.append(
            f"To: {draft.recipient_name}"
        )

    lines.append(
        f"Subject: {draft.subject}"
    )

    lines.append("")

    lines.append(
        draft.body,
    )

    lines.append("")

    if draft.sender_name:

        lines.append(
            draft.sender_name,
        )

    if draft.sender_email:

        lines.append(
            draft.sender_email,
        )

    if draft.sender_mobile:

        lines.append(
            draft.sender_mobile,
        )

    if draft.attachment_required:

        lines.append("")

        lines.append(
            "Attachment: Resume",
        )

    return "\n".join(
        lines,
    )


# ============================================================
# Persist Conversation
# ============================================================


async def persist_conversation(
    state: AgentGraphState,
) -> dict[str, Any]:

    user_id = state["user_id"]

    await session_manager.add_message(
        user_id=user_id,
        role="user",
        content=state["message"],
    )

    await session_manager.add_message(
        user_id=user_id,
        role="assistant",
        content=state["answer"],
    )

    return {}


# ============================================================
# Metadata
# ============================================================


def build_metadata(
    state: AgentGraphState,
) -> dict[str, Any]:

    route_result = state["route_result"]

    session = state["session"]

    active_jd = state.get(
        "active_jd",
    )

    analysis = state.get(
        "jd_analysis",
    )

    match = state.get(
        "jd_match",
    )

    metadata: dict[str, Any] = {
        "intent": route_result.intent.value,
        "routing_confidence": (
            route_result.confidence
        ),
        "active_jd_id": (
            active_jd.jd_id
            if active_jd
            else None
        ),
        "available_jd_ids": list(
            session.jd_contexts.keys()
        ),
    }

    # ========================================================
    # Newly detected JD
    # ========================================================

    if state.get("detected_jd_id"):

        metadata["detected_new_jd"] = {
            "jd_id": state.get(
                "detected_jd_id",
            ),
            "title": state.get(
                "detected_jd_title",
            ),
            "company": state.get(
                "detected_jd_company",
            ),
            "confidence": state.get(
                "detected_jd_confidence",
            ),
        }

    # ========================================================
    # JD Intelligence
    # ========================================================

    if analysis is not None:

        metadata["jd_intelligence"] = {
            "required_skills": (
                analysis.required_skills
            ),
            "preferred_skills": (
                analysis.preferred_skills
            ),
            "responsibilities": (
                analysis.responsibilities
            ),
        }

    if match is not None:

        metadata["jd_match"] = {
            "matched_skills": (
                match.matched_skills
            ),
            "missing_required_skills": (
                match.missing_required_skills
            ),
        }

    # ========================================================
    # Email Draft Metadata
    # ========================================================

    email_draft = state.get(
        "email_draft",
    )

    if email_draft is not None:

        metadata["email_draft"] = {
            "recipient_email": (
                email_draft.recipient_email
            ),
            "recipient_name": (
                email_draft.recipient_name
            ),
            "subject": (
                email_draft.subject
            ),
            "sender_name": (
                email_draft.sender_name
            ),
            "sender_email": (
                email_draft.sender_email
            ),
            "sender_mobile": (
                email_draft.sender_mobile
            ),
            "attachment_required": (
                email_draft.attachment_required
            ),
            "attachment_type": (
                email_draft.attachment_type
            ),
        }

    # ========================================================
    # Email Send Metadata
    # ========================================================

    if state.get("email_send_result") is not None:

        metadata["email_sent"] = True

        metadata["email_record_id"] = (
            state.get(
                "email_record_id",
            )
        )

    return metadata


# ============================================================
# Check Email Connection
# ============================================================


async def check_email_connection(
    state: AgentGraphState,
) -> dict[str, Any]:

    user_id = state["user_id"]

    connection = (
        await email_connection_service.check_connection(
            user_id,
        )
    )

    if not connection.connected:

        logger.info(
            "Email not connected: user=%s",
            user_id,
        )

        return {
            "email_connection": {
                "connected": False,
                "provider": connection.provider,
                "email_address": (
                    connection.email_address
                ),
                "connection_id": (
                    str(
                        connection.connection_id
                    )
                    if connection.connection_id
                    else None
                ),
            },
        }

    credentials = (
        await email_connection_service.get_credentials(
            user_id,
        )
    )

    logger.info(
        "Email connection verified: "
        "user=%s provider=%s",
        user_id,
        credentials.provider,
    )

    return {
        "email_connection": {
            "connected": True,
            "provider": credentials.provider,
            "email_address": (
                credentials.email_address
            ),
            "connection_id": str(
                credentials.connection_id,
            ),
            "expires_at": (
                credentials.expires_at
            ),
        },
        "email_credentials": credentials,
    }


# ============================================================
# Email Not Connected
# ============================================================


def email_not_connected(
    state: AgentGraphState,
) -> dict[str, Any]:
    """
    Stop the email flow when the user has not connected
    their email account.
    """

    return {
        "answer": (
            "Your Gmail account is not connected. "
            "Please connect your Gmail account from "
            "your Profile before using email features."
        ),
    }