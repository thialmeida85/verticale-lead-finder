from collections import Counter
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from . import models, schemas
from .cnpj_api import CnpjApiError, consultar_cnpj_api
from .utils import normalize_cnpj, normalize_phone


BAD_SITUATIONS = {"baixada", "inapta", "suspensa"}


def calculate_score(company: dict) -> int:
    if company.get("nao_contatar"):
        return 0

    situacao = str(company.get("situacao_cadastral") or "").lower()
    if any(term in situacao for term in BAD_SITUATIONS):
        return 0

    score = 0
    if "ativa" in situacao or situacao == "2":
        score += 20
    if str(company.get("matriz_filial") or "").lower() == "matriz":
        score += 10
    if company.get("telefone_principal"):
        score += 20
    else:
        score -= 30
    if company.get("email"):
        score += 10
    if str(company.get("porte") or "").upper() in {"ME", "EPP"} or any(term in str(company.get("porte") or "").upper() for term in ["MICRO", "PEQUENO"]):
        score += 10
    if company.get("capital_social") and company["capital_social"] > 20000:
        score += 10
    if company.get("cnae_principal"):
        score += 10
    if company.get("cidade"):
        score += 10
    return max(0, min(score, 100))


def normalize_lead_payload(payload: dict) -> dict:
    data = dict(payload)
    data["cnpj"] = normalize_cnpj(data.get("cnpj"))
    data["telefone_1"] = normalize_phone(data.get("telefone_1"))
    data["telefone_2"] = normalize_phone(data.get("telefone_2"))
    data["telefone_principal"] = normalize_phone(data.get("telefone_principal")) or data["telefone_1"] or data["telefone_2"]
    data["tem_telefone"] = bool(data.get("telefone_principal"))
    data["tem_email"] = bool(data.get("email"))
    data["possivel_whatsapp"] = bool(data.get("telefone_principal"))
    data["segmento"] = data.get("segmento") or data.get("cnae_descricao")
    data["status_lead"] = data.get("status_lead") or "novo"
    data["tags"] = normalize_tags(data.get("tags"))
    data["data_consulta"] = data.get("data_consulta") or datetime.now(timezone.utc)
    data["score"] = calculate_score(data)
    return data


def normalize_tags(value) -> list[str] | None:
    if value in (None, "", []):
        return None
    if isinstance(value, str):
        tags = [tag.strip() for tag in value.split(",") if tag.strip()]
        return tags or None
    if isinstance(value, list):
        return [str(tag).strip() for tag in value if str(tag).strip()]
    return [str(value)]


async def consultar_empresas(db: Session, request: schemas.CnpjConsultaRequest) -> list[dict]:
    params = request.model_dump()
    try:
        results = await consultar_cnpj_api(params)
        results = [_with_score(normalize_lead_payload(result)) for result in results]
        filtered = _filter_result_dicts(results, request)
        log_consulta(db, "cnpj", params, len(filtered), "sucesso", None)
        return filtered[: request.limite]
    except CnpjApiError as exc:
        log_consulta(db, "cnpj", params, 0, "erro", str(exc))
        raise


def save_lead(db: Session, payload: schemas.LeadCreate) -> models.Lead:
    data = normalize_lead_payload(payload.model_dump())
    existing = db.scalar(select(models.Lead).where(models.Lead.cnpj == data["cnpj"]))
    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing

    lead = models.Lead(**data)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def list_leads(db: Session, filters: schemas.LeadFilter) -> list[models.Lead]:
    stmt = select(models.Lead)
    stmt = apply_lead_filters(stmt, filters)
    return list(db.scalars(stmt.order_by(models.Lead.score.desc(), models.Lead.updated_at.desc())))


def apply_lead_filters(stmt, filters: schemas.LeadFilter):
    if filters.q:
        term = f"%{filters.q}%"
        stmt = stmt.where(or_(models.Lead.razao_social.ilike(term), models.Lead.nome_fantasia.ilike(term), models.Lead.cnpj.ilike(term)))
    if filters.cidade:
        stmt = stmt.where(models.Lead.cidade.ilike(f"%{filters.cidade}%"))
    if filters.uf:
        stmt = stmt.where(models.Lead.uf == filters.uf.upper())
    if filters.segmento:
        stmt = stmt.where(models.Lead.segmento.ilike(f"%{filters.segmento}%"))
    if filters.cnae:
        stmt = stmt.where(models.Lead.cnae_principal.ilike(f"%{filters.cnae}%"))
    if filters.status_lead:
        stmt = stmt.where(models.Lead.status_lead == filters.status_lead)
    if filters.min_score is not None:
        stmt = stmt.where(models.Lead.score >= filters.min_score)
    if filters.tem_telefone is not None:
        stmt = stmt.where(models.Lead.tem_telefone == filters.tem_telefone)
    if filters.tem_email is not None:
        stmt = stmt.where(models.Lead.tem_email == filters.tem_email)
    if filters.possivel_whatsapp is not None:
        stmt = stmt.where(models.Lead.possivel_whatsapp == filters.possivel_whatsapp)
    if filters.nao_contatar is not None:
        stmt = stmt.where(models.Lead.nao_contatar == filters.nao_contatar)
    if filters.data_cadastro:
        stmt = stmt.where(models.Lead.created_at >= filters.data_cadastro)
    return stmt


def get_lead(db: Session, lead_id: UUID) -> models.Lead | None:
    return db.get(models.Lead, lead_id)


def update_lead(db: Session, lead_id: UUID, payload: schemas.LeadUpdate) -> models.Lead | None:
    lead = get_lead(db, lead_id)
    if not lead:
        return None

    for key, value in payload.model_dump(exclude_unset=True).items():
        if key == "tags":
            value = normalize_tags(value)
        setattr(lead, key, value)
    lead.score = calculate_score({column.name: getattr(lead, column.name) for column in models.Lead.__table__.columns})
    db.commit()
    db.refresh(lead)
    return lead


def delete_lead(db: Session, lead_id: UUID) -> bool:
    lead = get_lead(db, lead_id)
    if not lead:
        return False
    db.delete(lead)
    db.commit()
    return True


def dashboard_stats(db: Session) -> schemas.DashboardStats:
    leads = list(db.scalars(select(models.Lead)))
    return schemas.DashboardStats(
        total_leads=len(leads),
        leads_com_telefone=sum(1 for lead in leads if lead.tem_telefone),
        leads_com_email=sum(1 for lead in leads if lead.tem_email),
        leads_por_cidade=dict(Counter(lead.cidade or "Sem cidade" for lead in leads)),
        leads_por_uf=dict(Counter(lead.uf or "Sem UF" for lead in leads)),
        leads_por_status=dict(Counter(lead.status_lead or "novo" for lead in leads)),
        leads_score_alto=sum(1 for lead in leads if lead.score >= 81),
        leads_exportados=sum(1 for lead in leads if lead.exportado),
    )


def log_consulta(db: Session, tipo: str, parametros: dict, quantidade: int, status: str, erro: str | None):
    db.add(
        models.ConsultaApi(
            tipo_consulta=tipo,
            parametros=parametros,
            quantidade_resultados=quantidade,
            status=status,
            mensagem_erro=erro,
        )
    )
    db.commit()


def _with_score(data: dict) -> dict:
    data["score"] = calculate_score(data)
    return data


def _filter_result_dicts(results: list[dict], request: schemas.CnpjConsultaRequest) -> list[dict]:
    filtered = []
    for item in results:
        if request.somente_ativas and "ativa" not in str(item.get("situacao_cadastral") or "").lower():
            continue
        if request.somente_matriz and item.get("matriz_filial") != "matriz":
            continue
        if request.somente_com_telefone and not item.get("telefone_principal"):
            continue
        if request.uf and item.get("uf") != request.uf.upper():
            continue
        if request.cidade and request.cidade.lower() not in str(item.get("cidade") or "").lower():
            continue
        if request.cnae and request.cnae not in str(item.get("cnae_principal") or ""):
            continue
        if request.segmento and request.segmento.lower() not in str(item.get("segmento") or "").lower():
            continue
        if request.porte and request.porte.lower() not in str(item.get("porte") or "").lower():
            continue
        if request.termo:
            haystack = " ".join(str(item.get(key) or "") for key in ["razao_social", "nome_fantasia", "segmento", "cidade"])
            if request.termo.lower() not in haystack.lower():
                continue
        filtered.append(item)
    return filtered
