from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

# Importas tus firmas e implementaciones
from app.database import get_db
from app.models import Sector
from app.repositories.imp.SectorRepository import SectorRepository
from app.schemas import SectorSchema
from app.services.ISectorService import ISectorService
from app.services.imp.SectorService import SectorService

router = APIRouter(prefix="/sectores", tags=["Sectores"])

# Esta es la función de fábrica que resuelve las dependencias
def get_sector_service(db: Session = Depends(get_db)) -> ISectorService:
    repo = SectorRepository(db)
    return SectorService(repo)

@router.get("/web", response_model=List[SectorSchema])
async def get_sectores_web(
    service: ISectorService = Depends(get_sector_service)
):
    """
    Endpoint para el e-commerce: trae solo sectores con mostrar_en_web = True
    """
    return service.listar_sectores_para_ecommerce()