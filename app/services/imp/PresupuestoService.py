
from typing import Any
from fastapi import Depends
from app.database import get_db
from app.models.Presupuesto import Presupuesto
from app.repositories.imp.PresupuestoRepository import PresupuestoRepository
from repositories.IPresupuestoRepository import IPresupuestoRepository
from services.IPresupuestoService import IPresupuestoService
class PresupuestoService(IPresupuestoService):
    presupuestoRepository: IPresupuestoRepository

    def __init__(self, presupuestoRepository: IPresupuestoRepository):
        self.presupuestoRepository = presupuestoRepository

    def get_paginado(
        self, 
        skip: int, 
        limit: int, 
        cliente_id: Any = None,
        estado: Any = None,
        desde: Any = None,
        hasta: Any = None
    ):
        return self.presupuestoRepository.get_paginado(
            skip=skip,
            limit=limit,
            cliente_id=cliente_id,
            estado=estado,
            desde=desde,
            hasta=hasta
        )
    
    def crear(self, presupuesto: Any):
        return self.presupuestoRepository.crear(presupuesto)
    
    def get_by_id(self, presupuesto_id: int):
        return self.presupuestoRepository.get_by_id(presupuesto_id)
    
    def actualizar(self, presupuesto: Presupuesto) -> Presupuesto:
        return self.presupuestoRepository.actualizar(presupuesto)


def get_presupuesto_service(db: Any = Depends(get_db)) -> PresupuestoService:
    repository = PresupuestoRepository(db)
    return PresupuestoService(repository)