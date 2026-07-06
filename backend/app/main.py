from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from . import schemas
from .cnpj_api import CnpjApiError
from .config import get_settings
from .database import get_db
from .export_service import export_leads
from .lead_service import (
    consultar_empresas,
    dashboard_stats,
    delete_lead,
    get_lead,
    list_leads,
    save_lead,
    update_lead,
)


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/cnpj/consultar", response_model=list[schemas.LeadCreate])
async def api_consultar_cnpj(request: schemas.CnpjConsultaRequest, db: Session = Depends(get_db)):
    try:
        return await consultar_empresas(db, request)
    except CnpjApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@app.post("/api/leads", response_model=schemas.LeadRead)
def api_save_lead(request: schemas.LeadCreate, db: Session = Depends(get_db)):
    return save_lead(db, request)


@app.get("/api/leads", response_model=list[schemas.LeadRead])
def api_list_leads(
    q: str | None = None,
    cidade: str | None = None,
    uf: str | None = None,
    segmento: str | None = None,
    cnae: str | None = None,
    status_lead: str | None = None,
    min_score: int | None = None,
    tem_telefone: bool | None = None,
    tem_email: bool | None = None,
    possivel_whatsapp: bool | None = None,
    nao_contatar: bool | None = None,
    data_cadastro: str | None = None,
    db: Session = Depends(get_db),
):
    filters = schemas.LeadFilter(
        q=q,
        cidade=cidade,
        uf=uf,
        segmento=segmento,
        cnae=cnae,
        status_lead=status_lead,
        min_score=min_score,
        tem_telefone=tem_telefone,
        tem_email=tem_email,
        possivel_whatsapp=possivel_whatsapp,
        nao_contatar=nao_contatar,
        data_cadastro=data_cadastro,
    )
    return list_leads(db, filters)


@app.get("/api/leads/{lead_id}", response_model=schemas.LeadRead)
def api_get_lead(lead_id: UUID, db: Session = Depends(get_db)):
    lead = get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado.")
    return lead


@app.put("/api/leads/{lead_id}", response_model=schemas.LeadRead)
def api_update_lead(lead_id: UUID, request: schemas.LeadUpdate, db: Session = Depends(get_db)):
    lead = update_lead(db, lead_id, request)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado.")
    return lead


@app.delete("/api/leads/{lead_id}", status_code=204)
def api_delete_lead(lead_id: UUID, db: Session = Depends(get_db)):
    if not delete_lead(db, lead_id):
        raise HTTPException(status_code=404, detail="Lead não encontrado.")
    return Response(status_code=204)


@app.get("/api/dashboard", response_model=schemas.DashboardStats)
def api_dashboard(db: Session = Depends(get_db)):
    return dashboard_stats(db)


@app.post("/api/exportar/csv")
def api_export_csv(request: schemas.ExportRequest, db: Session = Depends(get_db)):
    path = export_leads(db, request, "csv")
    return FileResponse(path, filename=path.name)


@app.post("/api/exportar/xlsx")
def api_export_xlsx(request: schemas.ExportRequest, db: Session = Depends(get_db)):
    path = export_leads(db, request, "xlsx")
    return FileResponse(path, filename=path.name)
