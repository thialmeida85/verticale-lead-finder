import os


os.environ.setdefault("DATABASE_URL", "postgresql://user:password@localhost/dbname")

from app.cnpj_api import CANONICAL_COMPANY_FIELDS, canonical_company
from app.lead_service import calculate_score, normalize_lead_payload


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

    print("Backend smoke test OK: contrato CNPJ, normalização e score funcionando.")


if __name__ == "__main__":
    main()
