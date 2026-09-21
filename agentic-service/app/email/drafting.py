from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger


logger = get_logger(__name__)


# ============================================================
# Structured Email Draft
# ============================================================


class EmailDraft(BaseModel):
    """
    Structured email draft produced by the email agent.

    This is runtime data only.

    It is NOT persisted as an email record in Section 19.
    """

    recipient_email: str | None = None

    recipient_name: str | None = None

    subject: str = Field(
        min_length=1,
        max_length=200,
    )

    body: str = Field(
        min_length=1,
    )

    sender_name: str | None = None

    sender_email: str | None = None

    sender_mobile: str | None = None

    attachment_required: bool = True

    attachment_type: str | None = "resume"


# ============================================================
# Prompt
# ============================================================


EMAIL_DRAFT_SYSTEM_PROMPT = """
You are CareerForge's professional job-application email
drafting agent.

Your job is to create a concise, credible, personalised email
for a job opportunity using ONLY the information supplied in
the context.

The email is intended for a recruiter, hiring manager, or
appropriate hiring contact.

============================================================
CORE RULES
============================================================

1. The ACTIVE JOB DESCRIPTION is the primary job context.

2. Use the user's retrieved profile/resume information as the
   source of truth for candidate claims.

3. NEVER invent:
   - skills
   - years of experience
   - companies
   - job titles
   - projects
   - achievements
   - certifications
   - education
   - recruiter names
   - recruiter email addresses
   - candidate contact information

4. Only mention candidate experience when the supplied
   context supports it.

5. If the user's context does not support a claim, leave it out.

6. Do not convert a JD requirement into a claim that the
   candidate possesses that skill.

7. Do not say the candidate is "a perfect fit", "an ideal
   candidate", or similar unsupported claims.

8. Use the JD to identify the most relevant candidate evidence.

9. Prefer 1-3 highly relevant candidate strengths over a long
   list of technologies.

10. The email must be concise. Normally 120-180 words for the
    body unless the user's request clearly requires otherwise.

============================================================
EMAIL QUALITY
============================================================

The email should:

- have a natural professional tone
- sound like a real job applicant
- be specific to the role
- avoid generic mass-application language
- avoid unnecessary buzzwords
- avoid excessive self-praise
- avoid repeating the complete JD
- avoid repeating the complete resume
- make the reason for contacting the recipient clear
- have a clear call to action
- end professionally

The opening should identify the role being applied for when
the role title is available.

The middle should connect the candidate's strongest relevant
evidence to the role.

The closing should politely express interest in discussing the
opportunity.

============================================================
RECIPIENT
============================================================

If the user supplied a recipient email address, preserve it.

If the context contains a recipient email address, use it only
if it is clearly identified as the intended recipient.

Otherwise return recipient_email as null.

NEVER invent an email address.

If a recipient name is unavailable, use a neutral greeting such
as "Dear Hiring Team,".

============================================================
SENDER
============================================================

Use the candidate's name, email, and mobile number only when
supported by the supplied user context.

Do not invent missing contact information.

============================================================
RESUME
============================================================

The application is expected to include the user's resume.

Set:

attachment_required = true
attachment_type = "resume"

Do not claim that the resume has already been attached or sent.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Schema:

{
  "recipient_email": null,
  "recipient_name": null,
  "subject": "...",
  "body": "...",
  "sender_name": "...",
  "sender_email": "...",
  "sender_mobile": "...",
  "attachment_required": true,
  "attachment_type": "resume"
}

Do not wrap the JSON in markdown fences.
""".strip()


# ============================================================
# Prompt Builder
# ============================================================


def build_email_draft_prompt(
    *,
    user_message: str,
    active_jd: str,
    retrieved_context: str,
    conversation: str = "",
    jd_intelligence: str = "",
) -> str:

    sections: list[str] = []

    if active_jd:

        sections.append(
            f"""
ACTIVE JOB DESCRIPTION:

{active_jd}
""".strip()
        )

    if jd_intelligence:

        sections.append(
            f"""
JD INTELLIGENCE:

{jd_intelligence}
""".strip()
        )

    if retrieved_context:

        sections.append(
            f"""
USER PROFILE / RESUME EVIDENCE:

{retrieved_context}
""".strip()
        )

    if conversation:

        sections.append(
            f"""
RELEVANT CONVERSATION HISTORY:

{conversation}
""".strip()
        )

    sections.append(
        f"""
USER REQUEST:

{user_message}
""".strip()
    )

    sections.append(
        """
TASK:

Create the strongest truthful and personalised application
email possible from the supplied evidence.

Prioritise relevance over length.

Do not add information that is not supported by the context.

Return only the requested JSON object.
""".strip()
    )

    return "\n\n".join(
        sections,
    )


# ============================================================
# Email Drafting Service
# ============================================================


class EmailDraftingService:
    """
    Dedicated service for generating application emails.

    This service only drafts.

    It does NOT:
        - send email
        - call Gmail
        - create email records
        - modify EmailConnection
        - upload attachments
    """

    def __init__(
        self,
        llm: Any,
    ) -> None:

        self.llm = llm

    async def draft(
        self,
        *,
        user_message: str,
        active_jd: str,
        retrieved_context: str,
        conversation: str = "",
        jd_intelligence: str = "",
    ) -> EmailDraft:

        if not active_jd.strip():

            raise ValueError(
                "An active JD is required for email drafting.",
            )

        prompt = build_email_draft_prompt(
            user_message=user_message,
            active_jd=active_jd,
            retrieved_context=retrieved_context,
            conversation=conversation,
            jd_intelligence=jd_intelligence,
        )

        raw = await self.llm.generate(
            system_prompt=EMAIL_DRAFT_SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        draft = self._parse_response(
            raw,
        )

        logger.info(
            "Email draft generated: subject=%s recipient=%s",
            draft.subject,
            draft.recipient_email,
        )

        return draft

    @staticmethod
    def _parse_response(
        raw: str,
    ) -> EmailDraft:

        cleaned = raw.strip()

        # ----------------------------------------------------
        # Remove accidental markdown fences.
        # ----------------------------------------------------

        if cleaned.startswith(
            "```",
        ):

            cleaned = re.sub(
                r"^```(?:json)?\s*",
                "",
                cleaned,
                flags=re.IGNORECASE,
            )

            cleaned = re.sub(
                r"\s*```$",
                "",
                cleaned,
            )

            cleaned = cleaned.strip()

        # ----------------------------------------------------
        # Parse JSON.
        # ----------------------------------------------------

        try:

            data: Any = json.loads(
                cleaned,
            )

        except json.JSONDecodeError as exc:

            # ------------------------------------------------
            # Try extracting the first JSON object.
            # ------------------------------------------------

            match = re.search(
                r"\{.*\}",
                cleaned,
                flags=re.DOTALL,
            )

            if not match:

                raise ValueError(
                    "Email drafting model did not return "
                    "valid JSON.",
                ) from exc

            try:

                data = json.loads(
                    match.group(0),
                )

            except json.JSONDecodeError as nested_exc:

                raise ValueError(
                    "Unable to parse email draft JSON.",
                ) from nested_exc

        # ----------------------------------------------------
        # Validate structured output.
        # ----------------------------------------------------

        try:

            return EmailDraft.model_validate(
                data,
            )

        except Exception as exc:

            raise ValueError(
                "Email draft failed schema validation.",
            ) from exc


__all__ = [
    "EmailDraft",
    "EmailDraftingService",
    "EMAIL_DRAFT_SYSTEM_PROMPT",
    "build_email_draft_prompt",
]