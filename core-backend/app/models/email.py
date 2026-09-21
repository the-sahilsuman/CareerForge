from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import EmailProvider, EmailStatus


class Email(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "emails"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    application_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("applications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    connection_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("email_connections.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    from_email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )

    to_email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )

    subject: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    provider: Mapped[EmailProvider] = mapped_column(
        nullable=False,
    )

    provider_message_id: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    status: Mapped[EmailStatus] = mapped_column(
        default=EmailStatus.PENDING,
        nullable=False,
        index=True,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="emails",
    )

    application = relationship(
        "Application",
        back_populates="emails",
    )

    connection = relationship(
        "EmailConnection",
        back_populates="emails",
    )