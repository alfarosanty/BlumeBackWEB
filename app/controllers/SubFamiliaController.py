from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.imp.SubFamiliaRepository import SubFamiliaRepository
from app.schemas.SubfamiliaSchema import SubFamiliaSchema
from app.services.ISubFamiliaService import ISubFamiliaService
from app.services.imp.SubFamiliaService import SubFamiliaService


router = APIRouter(prefix="/subfamilias", tags=["SubFamilias"])

def get_subfamilia_service(db: Session = Depends(get_db)) -> ISubFamiliaService:
    return SubFamiliaService(SubFamiliaRepository(db))

@router.get("/web", response_model=List[SubFamiliaSchema])
async def get_subfamilias_web(service: ISubFamiliaService = Depends(get_subfamilia_service)):
    return service.listar_para_web()