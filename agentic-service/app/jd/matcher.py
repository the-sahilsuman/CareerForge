from __future__ import annotations

import re

from app.jd.models import (
    JDAnalysis,
    JDMatchResult,
)
from app.retrieval.models import RetrievedChunk


class JDMatcher:
    """
    Deterministic first-pass JD/profile matcher.

    The matcher does not claim that semantic similarity equals
    ownership of a skill.

    It uses explicit textual evidence from retrieved user
    context.
    """

    def match(
        self,
        *,
        analysis: JDAnalysis,
        chunks: list[RetrievedChunk],
    ) -> JDMatchResult:

        user_text = self._build_user_text(
            chunks,
        )

        normalised_user_text = (
            self._normalise(
                user_text,
            )
        )

        matched_skills: list[str] = []

        missing_required_skills: list[str] = []

        for skill in analysis.required_skills:

            if self._contains_term(
                normalised_user_text,
                skill,
            ):

                matched_skills.append(
                    skill,
                )

            else:

                missing_required_skills.append(
                    skill,
                )

        # Preferred skills are useful matches too, but are
        # deliberately not treated as "missing required".
        for skill in analysis.preferred_skills:

            if self._contains_term(
                normalised_user_text,
                skill,
            ):

                if skill not in matched_skills:

                    matched_skills.append(
                        skill,
                    )

        matching_keywords = [
            keyword
            for keyword in analysis.keywords
            if self._contains_term(
                normalised_user_text,
                keyword,
            )
        ]

        evidence = self._build_evidence(
            analysis=analysis,
            chunks=chunks,
        )

        return JDMatchResult(
            matched_skills=matched_skills,
            missing_required_skills=(
                missing_required_skills
            ),
            matching_keywords=matching_keywords,
            relevant_evidence=evidence,
        )

    @staticmethod
    def _build_user_text(
        chunks: list[RetrievedChunk],
    ) -> str:

        return "\n".join(
            chunk.text
            for chunk in chunks
            if chunk.text.strip()
        )

    @staticmethod
    def _normalise(
        text: str,
    ) -> str:

        return " ".join(
            text.lower()
            .strip()
            .split()
        )

    @staticmethod
    def _contains_term(
        text: str,
        term: str,
    ) -> bool:

        term = term.strip()

        if not term:
            return False

        # Multi-word phrases are checked literally.
        if " " in term:

            return (
                term.lower()
                in text.lower()
            )

        pattern = (
            r"(?<!\w)"
            + re.escape(
                term.lower(),
            )
            + r"(?!\w)"
        )

        return re.search(
            pattern,
            text.lower(),
        ) is not None

    @staticmethod
    def _build_evidence(
        *,
        analysis: JDAnalysis,
        chunks: list[RetrievedChunk],
        max_items: int = 5,
    ) -> list[str]:
        """
        Return short evidence snippets from retrieved user
        context that can be supplied to the LLM.

        The actual retrieved text remains the source of truth.
        """

        matched_terms = [
            *analysis.required_skills,
            *analysis.preferred_skills,
        ]

        evidence: list[str] = []

        for chunk in chunks:

            text = chunk.text.strip()

            if not text:
                continue

            normalised = text.lower()

            relevant = any(
                term.lower() in normalised
                for term in matched_terms
                if term.strip()
            )

            if not relevant:
                continue

            evidence.append(
                text[:1000],
            )

            if len(evidence) >= max_items:
                break

        return evidence