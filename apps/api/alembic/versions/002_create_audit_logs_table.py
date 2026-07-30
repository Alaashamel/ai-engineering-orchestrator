"""Create audit_logs table

Revision ID: 002
Revises: 001
Create Date: 2026-07-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("actor", sa.String(100), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(255), nullable=True),
        sa.Column("details", postgresql.JSON, nullable=True),
        sa.Column("phase", sa.String(50), nullable=True),
        sa.Column("outcome", sa.String(20), nullable=False, server_default=sa.text("'success'")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
