from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)
from app.models.enums import (
    EmailConnectionStatus,
    EmailProvider,
)


class EmailConnection(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "email_connections"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    provider: Mapped[EmailProvider] = mapped_column(
        nullable=False,
    )

    email_address: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )

    status: Mapped[EmailConnectionStatus] = (
        mapped_column(
            default=EmailConnectionStatus.ACTIVE,
            nullable=False,
        )
    )

    access_token_encrypted: Mapped[str | None] = (
        mapped_column(
            nullable=True,
        )
    )

    refresh_token_encrypted: Mapped[str | None] = (
        mapped_column(
            nullable=True,
        )
    )

    expires_at: Mapped[datetime | None] = (
        mapped_column(
            DateTime(timezone=True),
            nullable=True,
        )
    )

    user = relationship(
        "User",
        back_populates="email_connections",
    )

    emails = relationship(
        "Email",
        back_populates="connection",
    )