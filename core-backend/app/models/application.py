from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ApplicationStatus


class Application(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "applications"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    job_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    job_url: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
    )

    job_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    hr_email: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
    )

    status: Mapped[ApplicationStatus] = mapped_column(
        default=ApplicationStatus.TO_APPLY,
        nullable=False,
        index=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="applications",
    )

    events = relationship(
        "ApplicationEvent",
        back_populates="application",
        cascade="all, delete-orphan",
    )

    emails = relationship(
        "Email",
        back_populates="application",
    )
    