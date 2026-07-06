# Verticale Lead Finder

Aplicação para consultar CNPJs, salvar empresas como leads, pontuar oportunidades e exportar a base em CSV ou XLSX.

O backend usa Neon Postgres via `DATABASE_URL`. A string de conexão fica apenas no `.env`.

## Scripts rápidos

No Windows, use:

```bat
run-backend.bat
run-frontend.bat
```

## Deploy no Render + Neon

O arquivo `render.yaml` cria dois serviços no Render:

- `verticale-lead-finder-api`: FastAPI
- `verticale-lead-finder-web`: React/Vite estático

O banco fica no Neon. No Blueprint do Render, preencha:

```env
DATABASE_URL="postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require&channel_binding=require"
CNPJ_API_KEY="sua_chave_aqui"
CORS_ORIGINS="https://URL-DO-FRONTEND.onrender.com"
VITE_API_BASE_URL="https://URL-DA-API.onrender.com"
```

Use a connection string direta do Neon para migrations. A build da API roda `alembic upgrade head`.

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`.

Configure o `.env` com a connection string direta do Neon para migrations:

```env
DATABASE_URL="postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require&channel_binding=require"
```

Para o backend rodando normalmente, você pode usar a string direta ou pooled. Para migrations, prefira a direta.

### Ordem recomendada de validação

1. `GET /health`
2. `POST /api/cnpj/consultar`
3. Validar normalização em `backend/app/cnpj_api.py`
4. `POST /api/leads` sem duplicar CNPJ
5. `GET /api/leads` com filtros
6. `POST /api/exportar/csv` e `POST /api/exportar/xlsx`
7. `GET /api/dashboard`
8. Só então lapidar o frontend

Para testar o encanamento do backend sem depender de frontend:

```bash
cd backend
.venv\Scripts\python.exe smoke_backend.py
```

## Migrations

O schema é versionado com Alembic:

```bash
cd backend
alembic revision --autogenerate -m "descricao da mudanca"
alembic upgrade head
```

Não use `Base.metadata.create_all()` em produção. O Neon deve ser atualizado por migrations.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

A interface sobe em `http://localhost:5173`.

## Fluxo

1. Consulte um CNPJ na tela `Buscar empresas`.
2. A empresa é normalizada, pontuada e salva no SQLite.
3. Use `Leads salvos` para filtrar, editar status, marcar `não contatar`, observar e excluir.
4. Use `Exportar leads` para baixar CSV ou XLSX excluindo não contatar, descartados ou já abordados.

## Segurança

A chave da API de CNPJ fica somente no backend, em `CNPJ_API_KEY`. A `DATABASE_URL` também fica somente no backend. O frontend conversa apenas com a API FastAPI.

O arquivo `backend/app/cnpj_api.py` é um adaptador. Se a API de CNPJ mudar, mantenha os mesmos campos normalizados em `CANONICAL_COMPANY_FIELDS` para preservar o restante do sistema.
