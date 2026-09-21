from __future__ import annotations

from typing import Any


ROUTER_SYSTEM_PROMPT = """
You are the intent router for CareerForge.

Your job is ONLY to classify the user's latest message
and identify an existing JD when the user clearly refers
to one.

Available intents:

profile
- Questions about the user's skills, education,
  experience, projects, certifications, or profile.

resume
- Questions specifically about the user's resume,
  resume content, resume improvements, or resume sections.

jd_analysis
- Questions asking to understand, summarize, extract,
  or analyse a job description.

jd_match
- Questions asking how the user's profile/resume matches
  a job description or what skills are missing.

jd_switch
- User explicitly wants to switch the active job description.

email_draft
- User asks to draft, write, prepare, or improve a
  professional job-related email.
- Do NOT send the email.

email_send
- User explicitly asks CareerForge to send an email,
  apply by email, contact HR/recruiter, or send the
  drafted application email.
- This intent means an actual email should be sent.

general_career
- General career advice that does not require a specific
  profile or JD operation.

unknown
- The intent cannot be determined reliably.

IMPORTANT JD RULES:

1. You may ONLY return a jd_id from the AVAILABLE JDs list.

2. Never invent a JD ID.

3. If the user clearly refers to a listed company, title,
   or JD, return that JD's exact ID.

4. If the user says:
      "this job"
      "this role"
      "this company"
   and there is an active JD, return the active JD ID.

5. If the user says:
      "switch to Amazon"
      "go back to Google"
      "analyse the Microsoft role"
   select the matching JD from AVAILABLE JDs.

6. If the user says:
      "the other job"
      "the other role"
   only select another JD when the intended JD is
   unambiguous from the available JDs.

7. If the user asks to compare two JDs, identify the
   explicitly referenced JD when possible. The active JD
   remains available separately to the agent.

8. If no specific JD can be resolved, return null for jd_id.

9. The active JD is provided separately from the available
   JD list.

10. Do not answer the user's question.

11. Return ONLY valid JSON.

Expected JSON:

{
  "intent": "jd_match",
  "jd_id": "amazon-jd",
  "confidence": 0.95,
  "reasoning": "User explicitly refers to Amazon."
}
""".strip()


def build_router_prompt(
    *,
    message: str,
    active_jd_id: str | None,
    available_jds: list[dict[str, Any]] | None = None,
) -> str:
    """
    Build the routing prompt using only JDs that actually
    exist in the current chat session.
    """

    active_jd = (
        active_jd_id
        if active_jd_id
        else "none"
    )

    available_jds = (
        available_jds
        if available_jds is not None
        else []
    )

    if available_jds:

        jd_lines: list[str] = []

        for jd in available_jds:

            jd_id = jd.get(
                "jd_id",
                "",
            )

            title = jd.get(
                "title",
            )

            company = jd.get(
                "company",
            )

            description_parts = [
                f"ID: {jd_id}",
            ]

            if company:
                description_parts.append(
                    f"Company: {company}",
                )

            if title:
                description_parts.append(
                    f"Title: {title}",
                )

            jd_lines.append(
                " | ".join(description_parts),
            )

        available_section = "\n".join(
            jd_lines,
        )

    else:

        available_section = "none"

    return f"""
ACTIVE JD ID:
{active_jd}

AVAILABLE JDs:
{available_section}

USER MESSAGE:
{message}

Classify the user's intent and, when possible, select
the exact JD ID from AVAILABLE JDs.
""".strip()