from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CnpjConsultaRequest(BaseModel):
    cnpj: str | None = None
    termo: str | None = None
    cidade: str | None = None
    uf: str | None = None
    cnae: str | None = None
    segmento: str | None = None
    porte: str | None = None
    somente_ativas: bool = True
    somente_matriz: bool = False
    somente_com_telefone: bool = False
    limite: int = Field(default=20, ge=1, le=100)


class LeadBase(BaseModel):
    cnpj: str
    razao_social: str
    nome_fantasia: str | None = None
    situacao_cadastral: str | None = None
    matriz_filial: str | None = None
    data_abertura: str | None = None
    cnae_principal: str | None = None
    cnae_descricao: str | None = None
    cnaes_secundarios: list[dict] | None = None
    segmento: str | None = None
    porte: str | None = None
    natureza_juridica: str | None = None
    capital_social: float | None = None
    cep: str | None = None
    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    uf: str | None = None
    telefone_1: str | None = None
    telefone_2: str | None = None
    telefone_principal: str | None = None
    email: str | None = None
    fonte: str = "cnpj.ws"
    url_fonte: str | None = None
    data_consulta: datetime | None = None
    tem_telefone: bool = False
    tem_email: bool = False
    possivel_whatsapp: bool = False
    status_lead: str = "novo"
    score: int = Field(default=0, ge=0, le=100)
    observacoes: str | None = None
    tags: list[str] | None = None
    nao_contatar: bool = False
    exportado: bool = False


class LeadCreate(LeadBase):
    pass


class LeadRead(LeadBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadUpdate(BaseModel):
    status_lead: str | None = None
    observacoes: str | None = None
    tags: list[str] | str | None = None
    nao_contatar: bool | None = None


class LeadFilter(BaseModel):
    q: str | None = None
    cidade: str | None = None
    uf: str | None = None
    segmento: str | None = None
    cnae: str | None = None
    status_lead: str | None = None
    min_score: int | None = Field(default=None, ge=0, le=100)
    tem_telefone: bool | None = None
    tem_email: bool | None = None
    possivel_whatsapp: bool | None = None
    nao_contatar: bool | None = None
    apenas_cnpj: bool | None = None
    data_cadastro: str | None = None


class ExportRequest(LeadFilter):
    excluir_nao_contatar: bool = True
    excluir_descartados: bool = True
    excluir_ja_abordados: bool = False


class DashboardStats(BaseModel):
    total_leads: int
    leads_com_telefone: int
    leads_com_email: int
    leads_por_cidade: dict[str, int]
    leads_por_uf: dict[str, int]
    leads_por_status: dict[str, int]
    leads_score_alto: int
    leads_exportados: int


class ImportResult(BaseModel):
    arquivo: str | None = None
    importados: int
    atualizados: int
    ignorados: int
    erros: list[dict]


class ImportJobRead(BaseModel):
    id: UUID
    tipo: str
    arquivo: str | None = None
    status: str
    total: int
    processados: int
    importados: int
    atualizados: int
    enriquecidos: int
    ignorados: int
    erros: list[dict] | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
