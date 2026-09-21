from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import UserRole, UserStatus


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        String(8),
        unique=True,
        nullable=False,
        index=True,
    )

    cognito_sub: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    login_email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False,
        index=True,
    )

    role: Mapped[UserRole] = mapped_column(
        default=UserRole.USER,
        nullable=False,
        index=True,
    )

    status: Mapped[UserStatus] = mapped_column(
        default=UserStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    skills = relationship(
        "Skill",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    education = relationship(
        "Education",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    experience = relationship(
        "Experience",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    projects = relationship(
        "Project",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    certifications = relationship(
        "Certification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    resumes = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    applications = relationship(
        "Application",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    emails = relationship(
        "Email",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    email_connections = relationship(
        "EmailConnection",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    buckets = relationship(
        "Bucket",
        back_populates="user",
        cascade="all, delete-orphan",
    )