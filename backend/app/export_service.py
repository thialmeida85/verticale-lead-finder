from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from . import models, schemas
from .config import get_settings
from .lead_service import list_leads


DEFAULT_MESSAGE = (
    "Olá, tudo bem? Sou Thiago, da Agência Verticale. Encontrei sua empresa em uma "
    "pesquisa de negócios da região e acredito que podemos ajudar com site, presença "
    "digital e geração de orçamentos. Posso te mostrar uma ideia rápida?"
)


def export_leads(db: Session, request: schemas.ExportRequest, file_format: str) -> Path:
    settings = get_settings()
    settings.export_path.mkdir(parents=True, exist_ok=True)
    leads = _filter_exportable(list_leads(db, request), request)
    rows = [_export_row(lead) for lead in leads]

    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    path = settings.export_path / f"leads-{timestamp}.{file_format}"
    dataframe = pd.DataFrame(rows, columns=[
        "Nome",
        "Telefone",
        "Empresa",
        "CNPJ",
        "Segmento",
        "Cidade",
        "Estado",
        "E-mail",
        "Status",
        "Score",
        "Origem",
        "Mensagem personalizada",
    ])

    if file_format == "xlsx":
        dataframe.to_excel(path, index=False)
    else:
        dataframe.to_csv(path, index=False, encoding="utf-8-sig")

    for lead in leads:
        lead.exportado = True
    db.commit()
    return path


def _filter_exportable(leads: list[models.Lead], request: schemas.ExportRequest) -> list[models.Lead]:
    filtered = []
    for lead in leads:
        if request.excluir_nao_contatar and lead.nao_contatar:
            continue
        if request.excluir_descartados and lead.status_lead == "descartado":
            continue
        if request.excluir_ja_abordados and lead.status_lead == "abordado":
            continue
        filtered.append(lead)
    return filtered


def _export_row(lead: models.Lead) -> dict:
    return {
        "Nome": lead.nome_fantasia or lead.razao_social,
        "Telefone": lead.telefone_principal,
        "Empresa": lead.razao_social,
        "CNPJ": lead.cnpj,
        "Segmento": lead.segmento,
        "Cidade": lead.cidade,
        "Estado": lead.uf,
        "E-mail": lead.email,
        "Status": lead.status_lead,
        "Score": lead.score,
        "Origem": lead.fonte,
        "Mensagem personalizada": DEFAULT_MESSAGE,
    }
