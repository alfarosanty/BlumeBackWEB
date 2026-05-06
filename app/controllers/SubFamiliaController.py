from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import obtener_usuario_confirmado
from app.database import get_db
from app.models.Usuario import Usuario
from app.repositories.imp.SubFamiliaRepository import SubFamiliaRepository
from app.schemas.FamiliaSchema import FiltroWebDTO
from app.schemas.SubfamiliaSchema import SubFamiliaSchema
from app.services.ISubFamiliaService import ISubFamiliaService
from app.services.imp.SubFamiliaService import SubFamiliaService


router = APIRouter(prefix="/subfamilias", tags=["SubFamilias"])

def get_subfamilia_service(db: Session = Depends(get_db)) -> ISubFamiliaService:
    return SubFamiliaService(SubFamiliaRepository(db))

@router.get("/web", response_model=List[SubFamiliaSchema])
async def get_subfamilias_web(service: ISubFamiliaService = Depends(get_subfamilia_service), auth: Usuario = Depends(obtener_usuario_confirmado)):
    return service.listar_para_web()

@router.get("/sector/{sector_id}", response_model=list[SubFamiliaSchema])
def get_filtros_sector(sector_id: int, db: Session = Depends(get_db), auth: Usuario = Depends(obtener_usuario_confirmado)):
    repo = SubFamiliaRepository(db)
    service = SubFamiliaService(repo)
    
    filtros = service.obtener_chips_navegacion(sector_id)
    
    if not filtros:
        return []
        
    return filtros