from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.repositories.imp.SectorRepository import SectorRepository
from app.schemas import SectorSchema
from app.services.ISectorService import ISectorService
from app.services.imp.SectorService import SectorService

router = APIRouter(prefix="/sectores", tags=["Sectores"])

def get_sector_service(db: Session = Depends(get_db)) -> ISectorService:
    repo = SectorRepository(db)
    return SectorService(repo)

@router.get("/web", response_model=List[SectorSchema])
async def get_sectores_web(
    service: ISectorService = Depends(get_sector_service),
):
    """
    Endpoint para el e-commerce: trae solo sectores con mostrar_en_web = True
    """
    return service.listar_sectores_para_ecommerce()

@router.put("/{sector_id}", response_model=SectorSchema)
async def update_sector(
    sector_id: int,
    nombre: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    foto: Optional[UploadFile] = File(None),
    service: ISectorService = Depends(get_sector_service),
    db: Session = Depends(get_db)
):
    try:
        return await service.update_sector(
            db=db,
            sector_id=sector_id,
            nombre=nombre,
            descripcion=descripcion,
            archivo_foto=foto
        )
    except Exception as e:
        print(f"Error en update_sector: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))