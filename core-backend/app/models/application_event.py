from uuid import UUID

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ApplicationStatus


class ApplicationEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "application_events"

    application_id: Mapped[UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    previous_status: Mapped[ApplicationStatus | None] = mapped_column(
        nullable=True,
    )

    new_status: Mapped[ApplicationStatus] = mapped_column(
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )

    application = relationship(
        "Application",
        back_populates="events",
    )