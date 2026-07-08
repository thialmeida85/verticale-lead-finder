import os


os.environ.setdefault("DATABASE_URL", "postgresql://user:password@localhost/dbname")

from app.cnpj_api import CANONICAL_COMPANY_FIELDS, canonical_company
from app.lead_service import calculate_score, normalize_lead_payload
from app.pdf_import_service import CNPJ_PATTERN
from app.utils import is_valid_cnpj, normalize_mobile_for_export


def main():
    raw = {
        "cnpj": "00.000.000/0001-00",
        "razao_social": "EMPRESA EXEMPLO LTDA",
        "nome_fantasia": "EMPRESA EXEMPLO",
        "situacao_cadastral": "ATIVA",
        "porte": "ME",
        "cnae_principal": "6201501",
        "cnae_descricao": "Desenvolvimento de programas de computador sob encomenda",
        "cidade": "SAO JOSE DOS CAMPOS",
        "uf": "SP",
        "telefone_1": "(12) 39999-9999",
        "email": "contato@empresa.com.br",
        "matriz_filial": "matriz",
        "capital_social": 30000,
    }

    canonical = canonical_company(raw)
    missing = [field for field in CANONICAL_COMPANY_FIELDS if field not in canonical]
    assert not missing, f"Campos canônicos ausentes: {missing}"
    assert canonical["cnpj"] == "00000000000100"
    assert canonical["telefone_principal"] == "5512399999999"

    lead = normalize_lead_payload(canonical)
    assert lead["tem_telefone"] is True
    assert lead["tem_email"] is True
    assert calculate_score(lead) == 100
    assert normalize_mobile_for_export("551239999999") == "5512939999999"
    assert normalize_mobile_for_export("5512939999999") == "5512939999999"
    assert normalize_mobile_for_export("(12) 3999-9999") == "5512939999999"
    assert normalize_mobile_for_export("(12) 93999-9999") == "5512939999999"
    assert is_valid_cnpj("57.111.565/0001-63") is True
    assert is_valid_cnpj("84.584.416/0004-37") is True
    assert is_valid_cnpj("00.000.000/0001-00") is False
    assert CNPJ_PATTERN.search("57 . 111 . 565 / 0001 - 63")

    print("Backend smoke test OK: contrato CNPJ, normalização e score funcionando.")


if __name__ == "__main__":
    main()
