"""simplify resume storage

Revision ID: e1680932171d
Revises: 305d0ad68ae7
Create Date: 2026-09-13
"""

from alembic import op
import sqlalchemy as sa


revision = "e1680932171d"
down_revision = "305d0ad68ae7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. Remove the foreign key from resumes -> resume_versions
    # ---------------------------------------------------------

    op.drop_constraint(
        "resumes_active_version_id_fkey",
        "resumes",
        type_="foreignkey",
    )

    # ---------------------------------------------------------
    # 2. Remove active_version_id from resumes
    # ---------------------------------------------------------

    op.drop_column(
        "resumes",
        "active_version_id",
    )

    # ---------------------------------------------------------
    # 3. Now resume_versions can safely be removed
    # ---------------------------------------------------------

    op.drop_table("resume_versions")

    # ---------------------------------------------------------
    # 4. Add direct S3/file information to resumes
    # ---------------------------------------------------------

    op.add_column(
        "resumes",
        sa.Column(
            "file_name",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "resumes",
        sa.Column(
            "s3_key",
            sa.String(length=1024),
            nullable=True,
        ),
    )

    op.add_column(
        "resumes",
        sa.Column(
            "object_url",
            sa.String(length=2048),
            nullable=True,
        ),
    )

    op.add_column(
        "resumes",
        sa.Column(
            "content_type",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "resumes",
        sa.Column(
            "file_size",
            sa.Integer(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # Remove direct resume file fields
    # ---------------------------------------------------------

    op.drop_column("resumes", "file_size")
    op.drop_column("resumes", "content_type")
    op.drop_column("resumes", "object_url")
    op.drop_column("resumes", "s3_key")
    op.drop_column("resumes", "file_name")

    # ---------------------------------------------------------
    # Recreate resume_versions
    # ---------------------------------------------------------

    op.create_table(
        "resume_versions",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "resume_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "version_number",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "file_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "s3_key",
            sa.String(length=1024),
            nullable=False,
        ),
        sa.Column(
            "object_url",
            sa.String(length=2048),
            nullable=False,
        ),
        sa.Column(
            "content_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "file_size",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "processing_status",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.ForeignKeyConstraint(
            ["resume_id"],
            ["resumes.id"],
            ondelete="CASCADE",
        ),
    )

    # ---------------------------------------------------------
    # Recreate active_version_id
    # ---------------------------------------------------------

    op.add_column(
        "resumes",
        sa.Column(
            "active_version_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "resumes_active_version_id_fkey",
        "resumes",
        "resume_versions",
        ["active_version_id"],
        ["id"],
        ondelete="SET NULL",
    )