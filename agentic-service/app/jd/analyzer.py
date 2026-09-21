from __future__ import annotations

import json
from typing import Any

from app.agent.llm import get_llm_provider
from app.core.logging import get_logger
from app.jd.models import JDAnalysis
from app.memory.models import JDContext


logger = get_logger(__name__)


JD_ANALYZER_SYSTEM_PROMPT = """
You are the JD intelligence component of CareerForge.

Your task is to analyse a job description and extract only
information supported by that job description.

Return ONLY valid JSON.

Required JSON structure:

{
  "summary": "...",
  "required_skills": [],
  "preferred_skills": [],
  "responsibilities": [],
  "experience_requirements": [],
  "education_requirements": [],
  "keywords": []
}

Rules:

1. Do not invent requirements.
2. Do not infer requirements that are not reasonably stated.
3. Keep required_skills and preferred_skills separate.
4. Keep responsibilities concise.
5. Keep experience requirements factual.
6. Keep education requirements factual.
7. Keywords should contain useful technical/professional terms
   explicitly present or clearly central to the JD.
8. Return JSON only.
""".strip()


class JDAnalyzer:
    """
    Analyse a JD using the configured LLM provider.

    The analyzer does not persist anything.
    """

    def __init__(
        self,
        llm=None,
    ) -> None:

        self.llm = (
            llm
            if llm is not None
            else get_llm_provider()
        )

    async def analyze(
        self,
        jd: JDContext,
    ) -> JDAnalysis:
        """
        Analyse one JD.
        """

        if not jd.description.strip():

            return JDAnalysis(
                jd_id=jd.jd_id,
                title=jd.title,
                company=jd.company,
                summary="No JD description is available.",
            )

        prompt = self._build_prompt(
            jd,
        )

        raw = await self.llm.generate(
            system_prompt=JD_ANALYZER_SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        data = self._parse_json(
            raw,
        )

        return JDAnalysis(
            jd_id=jd.jd_id,
            title=jd.title,
            company=jd.company,
            summary=self._string_value(
                data.get("summary"),
            ),
            required_skills=self._string_list(
                data.get("required_skills"),
            ),
            preferred_skills=self._string_list(
                data.get("preferred_skills"),
            ),
            responsibilities=self._string_list(
                data.get("responsibilities"),
            ),
            experience_requirements=self._string_list(
                data.get("experience_requirements"),
            ),
            education_requirements=self._string_list(
                data.get("education_requirements"),
            ),
            keywords=self._string_list(
                data.get("keywords"),
            ),
        )

    @staticmethod
    def _build_prompt(
        jd: JDContext,
    ) -> str:

        title = jd.title or "Not provided"

        company = jd.company or "Not provided"

        return f"""
JOB ID:
{jd.jd_id}

COMPANY:
{company}

TITLE:
{title}

JOB DESCRIPTION:
{jd.description}

Extract the structured JD information according to the
system instructions.
""".strip()

    @staticmethod
    def _parse_json(
        raw: str,
    ) -> dict[str, Any]:

        cleaned = raw.strip()

        if cleaned.startswith("```"):

            cleaned = (
                cleaned
                .replace(
                    "```json",
                    "",
                )
                .replace(
                    "```",
                    "",
                )
                .strip()
            )

        try:

            data = json.loads(
                cleaned,
            )

        except json.JSONDecodeError as exc:

            logger.warning(
                "JD analyzer returned invalid JSON: %s",
                exc,
            )

            raise ValueError(
                "JD analyzer returned invalid JSON."
            ) from exc

        if not isinstance(data, dict):

            raise ValueError(
                "JD analyzer returned a non-object JSON value."
            )

        return data

    @staticmethod
    def _string_value(
        value: Any,
    ) -> str:

        if value is None:
            return ""

        return str(value).strip()

    @staticmethod
    def _string_list(
        value: Any,
    ) -> list[str]:

        if not isinstance(value, list):
            return []

        result: list[str] = []

        for item in value:

            if item is None:
                continue

            text = str(item).strip()

            if text:
                result.append(text)

        return result