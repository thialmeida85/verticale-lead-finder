"""add import jobs

Revision ID: 20260706_0002
Revises: 20260706_0001
Create Date: 2026-07-06
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260706_0002"
down_revision = "20260706_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "import_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tipo", sa.String(length=40), nullable=False),
        sa.Column("arquivo", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="pendente"),
        sa.Column("total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("processados", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("importados", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("atualizados", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enriquecidos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ignorados", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("erros", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_import_jobs_id", "import_jobs", ["id"])
    op.create_index("ix_import_jobs_tipo", "import_jobs", ["tipo"])
    op.create_index("ix_import_jobs_status", "import_jobs", ["status"])


def downgrade():
    op.drop_index("ix_import_jobs_status", table_name="import_jobs")
    op.drop_index("ix_import_jobs_tipo", table_name="import_jobs")
    op.drop_index("ix_import_jobs_id", table_name="import_jobs")
    op.drop_table("import_jobs")
