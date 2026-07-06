import json
from datetime import datetime, timezone

import httpx

from .config import get_settings
from .utils import normalize_cnpj, normalize_phone, parse_money


CANONICAL_COMPANY_FIELDS = [
    "cnpj",
    "razao_social",
    "nome_fantasia",
    "situacao_cadastral",
    "matriz_filial",
    "data_abertura",
    "cnae_principal",
    "cnae_descricao",
    "cnaes_secundarios",
    "segmento",
    "porte",
    "natureza_juridica",
    "capital_social",
    "cep",
    "logradouro",
    "numero",
    "complemento",
    "bairro",
    "cidade",
    "uf",
    "telefone_1",
    "telefone_2",
    "telefone_principal",
    "email",
    "fonte",
    "url_fonte",
    "data_consulta",
]


class CnpjApiError(RuntimeError):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


async def consultar_cnpj_api(params: dict) -> list[dict]:
    """Adapter boundary: translate any provider into CANONICAL_COMPANY_FIELDS."""
    cnpj = normalize_cnpj(params.get("cnpj"))
    if cnpj:
        return [await fetch_company(cnpj)]

    # The default public provider configured here only supports lookup by CNPJ.
    # The rest of the app still accepts filter searches so a paid/provider API can
    # be dropped into this adapter without changing services, schemas or screens.
    searchable = {key: value for key, value in params.items() if value not in (None, "", False)}
    if searchable:
        return []
    raise CnpjApiError("Informe um CNPJ ou configure uma API de busca por filtros.")


async def fetch_company(cnpj: str) -> dict:
    settings = get_settings()
    digits = normalize_cnpj(cnpj)
    if len(digits) != 14:
        raise CnpjApiError("CNPJ inválido. Informe 14 dígitos.")

    headers = {}
    if settings.cnpj_api_key:
        headers["Authorization"] = f"Bearer {settings.cnpj_api_key}"

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(f"{settings.cnpj_api_base_url}/{digits}", headers=headers)

    if response.status_code == 404:
        raise CnpjApiError("Nenhum resultado encontrado para o CNPJ informado.", 404)
    if response.status_code == 429:
        raise CnpjApiError("Limite de requisições da API de CNPJ atingido.", 429)
    if response.is_error:
        raise CnpjApiError("API de CNPJ indisponível no momento.", 503)

    return normalize_company(response.json())


def normalize_company(payload: dict) -> dict:
    estabelecimento = payload.get("estabelecimento") or {}
    atividade = estabelecimento.get("atividade_principal") or {}
    atividades_secundarias = estabelecimento.get("atividades_secundarias") or []
    cidade = estabelecimento.get("cidade") or {}
    estado = estabelecimento.get("estado") or {}
    natureza = payload.get("natureza_juridica") or {}
    porte = payload.get("porte") or {}

    cnpj = (
        estabelecimento.get("cnpj")
        or f"{payload.get('cnpj_raiz', '')}{estabelecimento.get('cnpj_ordem', '')}{estabelecimento.get('cnpj_digito_verificador', '')}"
    )
    telefone_1 = normalize_phone("".join([estabelecimento.get("ddd1") or "", estabelecimento.get("telefone1") or ""]))
    telefone_2 = normalize_phone("".join([estabelecimento.get("ddd2") or "", estabelecimento.get("telefone2") or ""]))
    telefone_principal = telefone_1 or telefone_2
    cnae_codigo = str(atividade.get("codigo") or "")
    cnae_descricao = atividade.get("descricao")

    return canonical_company({
        "cnpj": normalize_cnpj(cnpj),
        "razao_social": payload.get("razao_social") or "",
        "nome_fantasia": estabelecimento.get("nome_fantasia"),
        "situacao_cadastral": estabelecimento.get("situacao_cadastral"),
        "matriz_filial": "matriz" if str(estabelecimento.get("tipo") or "").lower() in {"matriz", "1"} else "filial",
        "data_abertura": estabelecimento.get("data_inicio_atividade"),
        "cnae_principal": cnae_codigo,
        "cnae_descricao": cnae_descricao,
        "cnaes_secundarios": atividades_secundarias,
        "segmento": cnae_descricao,
        "porte": porte.get("descricao") if isinstance(porte, dict) else porte,
        "natureza_juridica": natureza.get("descricao") if isinstance(natureza, dict) else natureza,
        "capital_social": parse_money(payload.get("capital_social")),
        "cep": estabelecimento.get("cep"),
        "logradouro": estabelecimento.get("logradouro"),
        "numero": estabelecimento.get("numero"),
        "complemento": estabelecimento.get("complemento"),
        "bairro": estabelecimento.get("bairro"),
        "cidade": cidade.get("nome"),
        "uf": estado.get("sigla"),
        "telefone_1": telefone_1,
        "telefone_2": telefone_2,
        "telefone_principal": telefone_principal,
        "email": estabelecimento.get("email"),
        "fonte": "cnpj.ws",
        "url_fonte": f"https://publica.cnpj.ws/cnpj/{normalize_cnpj(cnpj)}",
        "data_consulta": datetime.now(timezone.utc),
    })


def canonical_company(data: dict) -> dict:
    canonical = {field: data.get(field) for field in CANONICAL_COMPANY_FIELDS}
    canonical["cnpj"] = normalize_cnpj(canonical.get("cnpj"))
    canonical["razao_social"] = canonical.get("razao_social") or ""
    canonical["telefone_1"] = normalize_phone(canonical.get("telefone_1"))
    canonical["telefone_2"] = normalize_phone(canonical.get("telefone_2"))
    canonical["telefone_principal"] = normalize_phone(canonical.get("telefone_principal")) or canonical["telefone_1"] or canonical["telefone_2"]
    if isinstance(canonical.get("cnaes_secundarios"), str):
        try:
            canonical["cnaes_secundarios"] = json.loads(canonical["cnaes_secundarios"])
        except json.JSONDecodeError:
            canonical["cnaes_secundarios"] = []
    canonical["segmento"] = canonical.get("segmento") or canonical.get("cnae_descricao")
    canonical["fonte"] = canonical.get("fonte") or "cnpj_api"
    canonical["data_consulta"] = canonical.get("data_consulta") or datetime.now(timezone.utc)
    return canonical
