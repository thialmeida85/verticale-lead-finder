import asyncio
import io
import re
from datetime import datetime, timedelta, timezone
from uuid import UUID

from pypdf import PdfReader
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from . import models, schemas
from .cnpj_api import CnpjApiError, fetch_company
from .config import get_settings
from .database import SessionLocal
from .lead_service import save_lead
from .utils import is_valid_cnpj, only_digits


CNPJ_PATTERN = re.compile(r"(?<!\d)(?:\d[\s./-]*){14}(?!\d)")
FINISHED_STATUSES = {"concluido", "pausado_limite_api", "erro"}
STALE_PROCESSING_AFTER = timedelta(hours=12)


def create_pdf_import_job(db: Session, content: bytes, filename: str | None = None) -> tuple[models.ImportJob, list[str]]:
    cnpjs, diagnostics = extract_cnpjs_from_pdf(content)
    errors = []
    status = "pendente"
    if not cnpjs:
        status = "erro"
        if diagnostics["text_chars"] == 0:
            message = "Nenhum texto foi encontrado no PDF. Ele pode estar escaneado como imagem."
        else:
            message = "Nenhum CNPJ válido foi encontrado no texto extraído do PDF."
        errors.append({"item": "PDF", "erro": f"{message} Páginas: {diagnostics['pages']}. Caracteres lidos: {diagnostics['text_chars']}."})

    job = models.ImportJob(
        tipo="pdf",
        arquivo=filename,
        status=status,
        total=len(cnpjs),
        erros=errors,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job, cnpjs


def get_import_job(db: Session, job_id: UUID) -> models.ImportJob | None:
    _mark_stale_import_jobs(db)
    return db.get(models.ImportJob, job_id)


def list_import_jobs(db: Session, limit: int = 10) -> list[models.ImportJob]:
    _mark_stale_import_jobs(db)
    stmt = (
        select(models.ImportJob)
        .where(models.ImportJob.tipo == "pdf")
        .order_by(models.ImportJob.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


def clear_finished_import_jobs(db: Session) -> int:
    result = db.execute(
        delete(models.ImportJob).where(
            models.ImportJob.tipo == "pdf",
            models.ImportJob.status.in_(FINISHED_STATUSES),
        )
    )
    db.commit()
    return result.rowcount or 0


def _mark_stale_import_jobs(db: Session):
    cutoff = datetime.now(timezone.utc) - STALE_PROCESSING_AFTER
    jobs = list(
        db.scalars(
            select(models.ImportJob).where(
                models.ImportJob.tipo == "pdf",
                models.ImportJob.status == "processando",
                models.ImportJob.updated_at < cutoff,
            )
        )
    )
    if not jobs:
        return
    for job in jobs:
        job.status = "erro"
        _append_job_error(job, "PDF", "Importação interrompida antes de concluir. Inicie a importação novamente.")
    db.commit()


async def process_pdf_import_job(job_id: UUID, cnpjs: list[str]):
    if not cnpjs:
        with SessionLocal() as db:
            job = db.get(models.ImportJob, job_id)
            if job:
                job.status = "erro"
                job.total = 0
                if not job.erros:
                    job.erros = [{"item": "PDF", "erro": "Nenhum CNPJ foi encontrado para processar."}]
                db.commit()
        return

    settings = get_settings()
    with SessionLocal() as db:
        job = db.get(models.ImportJob, job_id)
        if not job:
            return
        job.erros = []
        job.status = "processando"
        job.total = len(cnpjs)
        db.commit()

    for cnpj in cnpjs:
        with SessionLocal() as db:
            job = db.get(models.ImportJob, job_id)
            if not job or job.status != "processando":
                break
        await _process_one_cnpj(job_id, cnpj)
        await asyncio.sleep(settings.cnpj_enrich_delay_seconds)

    with SessionLocal() as db:
        job = db.get(models.ImportJob, job_id)
        if job and job.status == "processando":
            job.status = "concluido"
            db.commit()


def extract_cnpjs_from_pdf(content: bytes) -> tuple[list[str], dict[str, int]]:
    reader = PdfReader(io.BytesIO(content))
    cnpjs = []
    seen = set()
    text_chars = 0

    for page in reader.pages:
        text = page.extract_text() or ""
        text_chars += len(text)
        for match in CNPJ_PATTERN.findall(text):
            digits = only_digits(match)
            if is_valid_cnpj(digits) and digits not in seen:
                seen.add(digits)
                cnpjs.append(digits)

    return cnpjs, {"pages": len(reader.pages), "text_chars": text_chars}


async def _process_one_cnpj(job_id: UUID, cnpj: str):
    with SessionLocal() as db:
        job = db.get(models.ImportJob, job_id)
        if not job:
            return
        existed = db.scalar(select(models.Lead.id).where(models.Lead.cnpj == cnpj)) is not None
        try:
            if not existed:
                save_lead(db, _placeholder_lead(cnpj))
                job = db.get(models.ImportJob, job_id)
                job.importados += 1
            else:
                job.atualizados += 1
            job.processados += 1
            db.commit()
        except Exception as exc:
            _append_job_error(job, cnpj, f"Erro ao salvar CNPJ provisório: {exc}")
            job.ignorados += 1
            job.processados += 1
            db.commit()
            return

    try:
        company = await fetch_company(cnpj)
    except CnpjApiError as exc:
        with SessionLocal() as db:
            job = db.get(models.ImportJob, job_id)
            if job:
                if exc.status_code == 429:
                    job.status = "pausado_limite_api"
                _append_job_error(job, cnpj, str(exc))
                db.commit()
        return

    with SessionLocal() as db:
        job = db.get(models.ImportJob, job_id)
        if not job:
            return
        try:
            save_lead(db, schemas.LeadCreate(**company, status_lead="novo"))
            job = db.get(models.ImportJob, job_id)
            job.enriquecidos += 1
            db.commit()
        except Exception as exc:
            _append_job_error(job, cnpj, f"Erro ao enriquecer lead: {exc}")
            db.commit()


def _placeholder_lead(cnpj: str) -> schemas.LeadCreate:
    return schemas.LeadCreate(
        cnpj=cnpj,
        razao_social=f"CNPJ {cnpj}",
        fonte="pdf_import",
        status_lead="importado",
        tags=["pdf"],
    )


def _append_job_error(job: models.ImportJob, cnpj: str, message: str):
    errors = list(job.erros or [])
    errors.append({"cnpj": cnpj, "erro": message})
    job.erros = errors[:100]
