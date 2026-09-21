from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class JDAnalysis:
    """
    Structured understanding of one job description.

    This object is runtime context only.
    It is not persisted as a new database model.
    """

    jd_id: str

    title: str | None = None

    company: str | None = None

    summary: str = ""

    required_skills: list[str] = field(
        default_factory=list,
    )

    preferred_skills: list[str] = field(
        default_factory=list,
    )

    responsibilities: list[str] = field(
        default_factory=list,
    )

    experience_requirements: list[str] = field(
        default_factory=list,
    )

    education_requirements: list[str] = field(
        default_factory=list,
    )

    keywords: list[str] = field(
        default_factory=list,
    )


@dataclass(slots=True)
class JDMatchResult:
    """
    Runtime comparison between a JD and the user's
    retrieved profile/resume context.
    """

    matched_skills: list[str] = field(
        default_factory=list,
    )

    missing_required_skills: list[str] = field(
        default_factory=list,
    )

    matching_keywords: list[str] = field(
        default_factory=list,
    )

    relevant_evidence: list[str] = field(
        default_factory=list,
    )

    def as_text(self) -> str:
        """
        Convert the match result into compact LLM context.
        """

        sections: list[str] = []

        if self.matched_skills:
            sections.append(
                "MATCHED SKILLS:\n"
                + "\n".join(
                    f"- {skill}"
                    for skill in self.matched_skills
                )
            )

        if self.missing_required_skills:
            sections.append(
                "MISSING REQUIRED SKILLS:\n"
                + "\n".join(
                    f"- {skill}"
                    for skill in self.missing_required_skills
                )
            )

        if self.matching_keywords:
            sections.append(
                "MATCHING KEYWORDS:\n"
                + "\n".join(
                    f"- {keyword}"
                    for keyword in self.matching_keywords
                )
            )

        if self.relevant_evidence:
            sections.append(
                "RELEVANT USER EVIDENCE:\n"
                + "\n".join(
                    f"- {evidence}"
                    for evidence in self.relevant_evidence
                )
            )

        return "\n\n".join(sections)