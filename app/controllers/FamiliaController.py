from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.imp.FamiliaRepository import FamiliaRepository
from app.schemas import FamiliaSchema, FiltroWebDTO
from app.services.IFamiliaService import IFamiliaService
from app.services.imp.FamiliaService import FamiliaService

router = APIRouter(prefix="/familias", tags=["Familias"])

def get_familia_service(db: Session = Depends(get_db)) -> IFamiliaService:
    return FamiliaService(FamiliaRepository(db))

@router.get("/web", response_model=List[FamiliaSchema])
async def get_familias_web(service: IFamiliaService = Depends(get_familia_service)):
    return service.listar_para_web()

@router.get("/sector/{sector_id}", response_model=list[FiltroWebDTO])
def get_filtros_sector(sector_id: int, db: Session = Depends(get_db)):
    repo = FamiliaRepository(db)
    service = FamiliaService(repo)
    
    filtros = service.obtener_chips_navegacion(sector_id)
    
    if not filtros:
        return []
        
    return filtros