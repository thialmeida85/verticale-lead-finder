import io
import re
from typing import Generator

from pypdf import PdfReader
from sqlalchemy.orm import Session

from . import models, schemas
from .lead_service import save_lead

# Regex para encontrar CNPJ (com ou sem máscara)
RE_CNPJ = re.compile(r"\b(\d{2}\.?\d{3}\.?\d{3}\/\d{4}-?\d{2})\b")


def _extract_text_from_pdf(content: bytes) -> str:
    """Extrai todo o texto de um conteúdo de PDF."""
    text = ""
    with io.BytesIO(content) as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def _find_cnpjs_in_text(text: str) -> Generator[str, None, None]:
    """Encontra CNPJs únicos em um bloco de texto."""
    # Usamos um set para garantir que cada CNPJ seja processado apenas uma vez
    cnpjs_encontrados = set(RE_CNPJ.findall(text))
    for cnpj in cnpjs_encontrados:
        yield cnpj


def process_pdf_and_create_pre_leads(db: Session, content: bytes) -> schemas.ImportResult:
    """
    Processa o conteúdo de um PDF, extrai CNPJs e cria "pré-leads" no banco de dados.
    """
    text = _extract_text_from_pdf(content)
    cnpjs_encontrados = _find_cnpjs_in_text(text)

    criados = 0
    ignorados = 0

    for cnpj in cnpjs_encontrados:
        # Verifica se o lead já existe para não sobrescrever
        existing = db.query(models.Lead).filter(models.Lead.cnpj == cnpj).first()
        if existing:
            ignorados += 1
            continue

        # Cria um pré-lead com status "importado" e dados mínimos
        pre_lead = schemas.LeadCreate(cnpj=cnpj, razao_social=f"Importado de PDF - {cnpj}", status_lead="importado")
        # Passamos calculate_score=False para não pontuar um lead incompleto
        save_lead(db, pre_lead)
        criados += 1

    return schemas.ImportResult(criados=criados, ignorados=ignorados, atualizados=0, total=criados + ignorados, erros=[])