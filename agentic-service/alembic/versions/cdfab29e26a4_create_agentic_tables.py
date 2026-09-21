"""create agentic email table

Revision ID: cdfab29e26a4
Revises:
Create Date: 2026-09-18
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "cdfab29e26a4"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create Agentic Service schema
    op.execute("CREATE SCHEMA IF NOT EXISTS agentic")

    # Email history / successfully sent applications
    op.create_table(
        "emails",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "hr_email",
            sa.String(length=320),
            nullable=False,
        ),
        sa.Column(
            "company_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="agentic",
    )

    op.create_index(
        "ix_agentic_emails_user_id",
        "emails",
        ["user_id"],
        unique=False,
        schema="agentic",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_agentic_emails_user_id",
        table_name="emails",
        schema="agentic",
    )

    op.drop_table(
        "emails",
        schema="agentic",
    )