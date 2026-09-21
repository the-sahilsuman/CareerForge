from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from typing import Any

from app.agent.llm import get_llm_provider
from app.core.logging import get_logger


logger = get_logger(__name__)


# ============================================================
# Result
# ============================================================


@dataclass(slots=True)
class JDExtractionResult:
    is_job_description: bool

    confidence: float

    jd_id: str | None = None

    title: str | None = None

    company: str | None = None

    description: str = ""


# ============================================================
# Prompt
# ============================================================


JD_EXTRACTION_SYSTEM_PROMPT = """
You are CareerForge's Job Description detection and extraction
component.

Your task is to inspect the user's latest message and determine
whether it contains a job description.

A message may contain BOTH:

1. a job description
2. an instruction such as:
   - send an email
   - draft an email
   - analyse this job
   - tell me if I am suitable
   - compare this role
   - apply for this role

The job description and the user instruction must be treated
as separate things.

IMPORTANT:

- Detect a JD only when the message actually contains a job
  description or substantial job-posting content.
- Do not treat ordinary career questions as a JD.
- Do not treat "send email to..." by itself as a JD.
- Do not invent company names.
- Do not invent job titles.
- If the company or title is not explicitly available, return
  null.
- Extract ONLY the job-description content.
- Do NOT include the user's command such as "send email".
- Preserve the important wording of the JD.
- Do not summarise the JD during extraction.
- Do not modify requirements.
- Do not invent missing content.

Return ONLY valid JSON.

Expected structure:

{
  "is_job_description": true,
  "confidence": 0.98,
  "title": "Software Engineer",
  "company": "Example Corp",
  "description": "complete extracted job description"
}

If no JD is present:

{
  "is_job_description": false,
  "confidence": 0.95,
  "title": null,
  "company": null,
  "description": ""
}
""".strip()


# ============================================================
# Extractor
# ============================================================


class JDExtractor:

    def __init__(
        self,
        llm=None,
    ) -> None:

        self.llm = (
            llm
            if llm is not None
            else get_llm_provider()
        )

    async def extract(
        self,
        message: str,
    ) -> JDExtractionResult:

        if not message.strip():

            return JDExtractionResult(
                is_job_description=False,
                confidence=1.0,
            )

        # ----------------------------------------------------
        # Cheap pre-check.
        #
        # Avoid an additional LLM call for clearly ordinary
        # short messages.
        # ----------------------------------------------------

        if not self._looks_like_jd(message):

            return JDExtractionResult(
                is_job_description=False,
                confidence=0.90,
            )

        prompt = f"""
USER MESSAGE:

{message}

Determine whether the message contains a job description.

If it does, extract the JD only.
Do not include the user's action/request outside the JD.

Return the required JSON object.
""".strip()

        raw = await self.llm.generate(
            system_prompt=JD_EXTRACTION_SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        result = self._parse(
            raw,
        )

        if not result.is_job_description:

            return result

        description = (
            result.description.strip()
        )

        if not description:

            return JDExtractionResult(
                is_job_description=False,
                confidence=result.confidence,
            )

        jd_id = (
            "jd_"
            + uuid.uuid4().hex
        )

        return JDExtractionResult(
            is_job_description=True,
            confidence=result.confidence,
            jd_id=jd_id,
            title=self._clean_optional(
                result.title,
            ),
            company=self._clean_optional(
                result.company,
            ),
            description=description,
        )

    @staticmethod
    def _looks_like_jd(
        message: str,
    ) -> bool:

        text = message.lower()

        jd_markers = [
            "job description",
            "responsibilities",
            "requirements",
            "qualifications",
            "required skills",
            "preferred skills",
            "what you'll do",
            "what you will do",
            "who you are",
            "experience required",
            "education",
            "about the role",
            "about the job",
            "skills and experience",
            "your responsibilities",
        ]

        marker_count = sum(
            1
            for marker in jd_markers
            if marker in text
        )

        # A substantial message containing JD language.
        if len(message) >= 600 and marker_count >= 1:
            return True

        # Shorter structured job posts.
        if len(message) >= 300 and marker_count >= 2:
            return True

        # Explicit JD heading.
        if re.search(
            r"\b(job description|jd)\s*:",
            text,
        ):
            return True

        return False

    @staticmethod
    def _clean_optional(
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        return value or None

    @staticmethod
    def _parse(
        raw: str,
    ) -> JDExtractionResult:

        cleaned = raw.strip()

        if cleaned.startswith("```"):

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

        try:

            data: Any = json.loads(
                cleaned,
            )

        except json.JSONDecodeError as exc:

            match = re.search(
                r"\{.*\}",
                cleaned,
                flags=re.DOTALL,
            )

            if not match:

                raise ValueError(
                    "JD extractor returned invalid JSON."
                ) from exc

            try:

                data = json.loads(
                    match.group(0),
                )

            except json.JSONDecodeError as nested_exc:

                raise ValueError(
                    "Unable to parse JD extractor response."
                ) from nested_exc

        if not isinstance(data, dict):

            raise ValueError(
                "JD extractor returned a non-object JSON value."
            )

        is_jd = bool(
            data.get(
                "is_job_description",
                False,
            )
        )

        try:

            confidence = float(
                data.get(
                    "confidence",
                    0.0,
                )
            )

        except (TypeError, ValueError):

            confidence = 0.0

        confidence = max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        )

        return JDExtractionResult(
            is_job_description=is_jd,
            confidence=confidence,
            title=data.get("title"),
            company=data.get("company"),
            description=str(
                data.get(
                    "description",
                    "",
                )
                or ""
            ),
        )


jd_extractor = JDExtractor()