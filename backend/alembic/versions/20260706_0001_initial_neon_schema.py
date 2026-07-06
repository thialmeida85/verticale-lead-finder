"""initial neon schema

Revision ID: 20260706_0001
Revises:
Create Date: 2026-07-06
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260706_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("cnpj", sa.String(length=20), nullable=False),
        sa.Column("razao_social", sa.String(length=255), nullable=False),
        sa.Column("nome_fantasia", sa.String(length=255), nullable=True),
        sa.Column("situacao_cadastral", sa.String(length=80), nullable=True),
        sa.Column("matriz_filial", sa.String(length=40), nullable=True),
        sa.Column("data_abertura", sa.String(length=20), nullable=True),
        sa.Column("cnae_principal", sa.String(length=30), nullable=True),
        sa.Column("cnae_descricao", sa.String(length=255), nullable=True),
        sa.Column("cnaes_secundarios", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("segmento", sa.String(length=120), nullable=True),
        sa.Column("porte", sa.String(length=80), nullable=True),
        sa.Column("natureza_juridica", sa.String(length=180), nullable=True),
        sa.Column("capital_social", sa.Float(), nullable=True),
        sa.Column("cep", sa.String(length=20), nullable=True),
        sa.Column("logradouro", sa.String(length=255), nullable=True),
        sa.Column("numero", sa.String(length=40), nullable=True),
        sa.Column("complemento", sa.String(length=120), nullable=True),
        sa.Column("bairro", sa.String(length=120), nullable=True),
        sa.Column("cidade", sa.String(length=120), nullable=True),
        sa.Column("uf", sa.String(length=2), nullable=True),
        sa.Column("telefone_1", sa.String(length=30), nullable=True),
        sa.Column("telefone_2", sa.String(length=30), nullable=True),
        sa.Column("telefone_principal", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("fonte", sa.String(length=80), nullable=False, server_default="cnpj.ws"),
        sa.Column("url_fonte", sa.String(length=255), nullable=True),
        sa.Column("data_consulta", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("tem_telefone", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("tem_email", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("possivel_whatsapp", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("status_lead", sa.String(length=60), nullable=False, server_default="novo"),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("nao_contatar", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("exportado", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_leads_cnpj", "leads", ["cnpj"], unique=True)
    op.create_index("ix_leads_razao_social", "leads", ["razao_social"])
    op.create_index("ix_leads_cidade", "leads", ["cidade"])
    op.create_index("ix_leads_uf", "leads", ["uf"])
    op.create_index("ix_leads_score", "leads", ["score"])
    op.create_index("ix_leads_status_lead", "leads", ["status_lead"])
    op.create_index("ix_leads_nao_contatar", "leads", ["nao_contatar"])

    op.create_table(
        "consultas_api",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tipo_consulta", sa.String(length=80), nullable=False),
        sa.Column("parametros", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("quantidade_resultados", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("mensagem_erro", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_consultas_api_tipo_consulta", "consultas_api", ["tipo_consulta"])
    op.create_index("ix_consultas_api_status", "consultas_api", ["status"])


def downgrade():
    op.drop_index("ix_consultas_api_status", table_name="consultas_api")
    op.drop_index("ix_consultas_api_tipo_consulta", table_name="consultas_api")
    op.drop_table("consultas_api")
    op.drop_index("ix_leads_nao_contatar", table_name="leads")
    op.drop_index("ix_leads_status_lead", table_name="leads")
    op.drop_index("ix_leads_score", table_name="leads")
    op.drop_index("ix_leads_uf", table_name="leads")
    op.drop_index("ix_leads_cidade", table_name="leads")
    op.drop_index("ix_leads_razao_social", table_name="leads")
    op.drop_index("ix_leads_cnpj", table_name="leads")
    op.drop_table("leads")
