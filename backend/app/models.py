import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    cnpj: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    razao_social: Mapped[str] = mapped_column(String(255), index=True)
    nome_fantasia: Mapped[str] = mapped_column(String(255), nullable=True)
    situacao_cadastral: Mapped[str] = mapped_column(String(80), nullable=True, index=True)
    matriz_filial: Mapped[str] = mapped_column(String(40), nullable=True, index=True)
    data_abertura: Mapped[str] = mapped_column(String(20), nullable=True)
    cnae_principal: Mapped[str] = mapped_column(String(30), nullable=True, index=True)
    cnae_descricao: Mapped[str] = mapped_column(String(255), nullable=True)
    cnaes_secundarios: Mapped[list] = mapped_column(JSONB, nullable=True)
    segmento: Mapped[str] = mapped_column(String(120), nullable=True, index=True)
    porte: Mapped[str] = mapped_column(String(80), nullable=True, index=True)
    natureza_juridica: Mapped[str] = mapped_column(String(180), nullable=True)
    capital_social: Mapped[float] = mapped_column(Float, nullable=True)
    cep: Mapped[str] = mapped_column(String(20), nullable=True)
    logradouro: Mapped[str] = mapped_column(String(255), nullable=True)
    numero: Mapped[str] = mapped_column(String(40), nullable=True)
    complemento: Mapped[str] = mapped_column(String(120), nullable=True)
    bairro: Mapped[str] = mapped_column(String(120), nullable=True)
    cidade: Mapped[str] = mapped_column(String(120), nullable=True, index=True)
    uf: Mapped[str] = mapped_column(String(2), nullable=True, index=True)
    telefone_1: Mapped[str] = mapped_column(String(30), nullable=True)
    telefone_2: Mapped[str] = mapped_column(String(30), nullable=True)
    telefone_principal: Mapped[str] = mapped_column(String(30), nullable=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    fonte: Mapped[str] = mapped_column(String(80), default="cnpj.ws")
    url_fonte: Mapped[str] = mapped_column(String(255), nullable=True)
    data_consulta: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    tem_telefone: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    tem_email: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    possivel_whatsapp: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    status_lead: Mapped[str] = mapped_column(String(60), default="novo", index=True)
    score: Mapped[int] = mapped_column(Integer, default=0, index=True)
    observacoes: Mapped[str] = mapped_column(Text, nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, nullable=True)
    nao_contatar: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    exportado: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class ConsultaApi(Base):
    __tablename__ = "consultas_api"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tipo_consulta: Mapped[str] = mapped_column(String(80), index=True)
    parametros: Mapped[dict] = mapped_column(JSONB)
    quantidade_resultados: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(60), index=True)
    mensagem_erro: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
