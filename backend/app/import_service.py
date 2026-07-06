import csv
import io

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .lead_service import save_lead
from .utils import only_digits, parse_money


FIELD_ALIASES = {
    "cnpj": ["cnpj", "documento", "cpf_cnpj"],
    "razao_social": ["razao_social", "razão social", "razao", "empresa", "nome_empresa", "nome"],
    "nome_fantasia": ["nome_fantasia", "fantasia", "nome fantasia"],
    "situacao_cadastral": ["situacao_cadastral", "situação cadastral", "situacao", "status_cadastral"],
    "matriz_filial": ["matriz_filial", "matriz/filial", "tipo"],
    "data_abertura": ["data_abertura", "abertura", "data_inicio_atividade"],
    "cnae_principal": ["cnae_principal", "cnae", "codigo_cnae", "cnae_codigo"],
    "cnae_descricao": ["cnae_descricao", "descricao_cnae", "descrição do cnae", "atividade", "atividade_principal"],
    "segmento": ["segmento", "setor", "categoria"],
    "porte": ["porte"],
    "natureza_juridica": ["natureza_juridica", "natureza jurídica"],
    "capital_social": ["capital_social", "capital"],
    "cep": ["cep"],
    "logradouro": ["logradouro", "endereco", "endereço", "rua"],
    "numero": ["numero", "número", "num"],
    "complemento": ["complemento"],
    "bairro": ["bairro"],
    "cidade": ["cidade", "municipio", "município"],
    "uf": ["uf", "estado"],
    "telefone_1": ["telefone_1", "telefone1", "telefone", "fone", "celular"],
    "telefone_2": ["telefone_2", "telefone2"],
    "telefone_principal": ["telefone_principal", "possivel_whatsapp", "whatsapp"],
    "email": ["email", "e-mail", "mail"],
    "observacoes": ["observacoes", "observações", "obs", "nota"],
    "tags": ["tags", "tag"],
}


def import_leads_csv(db: Session, content: bytes, filename: str | None = None) -> schemas.ImportResult:
    text = _decode_csv(content)
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;|\t")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)

    imported = 0
    updated = 0
    skipped = 0
    errors = []

    for line_number, row in enumerate(reader, start=2):
        payload = _map_row(row)
        cnpj = only_digits(payload.get("cnpj"))
        if not cnpj:
            skipped += 1
            errors.append({"linha": line_number, "erro": "CNPJ ausente ou inválido."})
            continue
        payload["cnpj"] = cnpj

        try:
            existed = db.scalar(select(models.Lead.id).where(models.Lead.cnpj == cnpj)) is not None
            save_lead(db, schemas.LeadCreate(**payload))
            if existed:
                updated += 1
            else:
                imported += 1
        except (ValidationError, ValueError) as exc:
            skipped += 1
            errors.append({"linha": line_number, "erro": str(exc)})

    return schemas.ImportResult(
        arquivo=filename,
        importados=imported,
        atualizados=updated,
        ignorados=skipped,
        erros=errors[:50],
    )


def _decode_csv(content: bytes) -> str:
    for encoding in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="ignore")


def _map_row(row: dict) -> dict:
    normalized_row = {_normalize_key(key): value for key, value in row.items()}
    payload = {"fonte": "csv_import"}

    for target, aliases in FIELD_ALIASES.items():
        value = _first_value(normalized_row, aliases)
        if value not in (None, ""):
            payload[target] = value.strip() if isinstance(value, str) else value

    if "capital_social" in payload:
        payload["capital_social"] = parse_money(payload["capital_social"])
    if "uf" in payload and payload["uf"]:
        payload["uf"] = str(payload["uf"]).upper()[:2]
    if "tags" in payload and isinstance(payload["tags"], str):
        payload["tags"] = [tag.strip() for tag in payload["tags"].split(",") if tag.strip()]

    return payload


def _first_value(row: dict, aliases: list[str]):
    for alias in aliases:
        value = row.get(_normalize_key(alias))
        if value not in (None, ""):
            return value
    return None


def _normalize_key(value: str | None) -> str:
    return (value or "").strip().lower().replace("-", "_").replace(" ", "_")
