
from typing import Any
from fastapi import Depends
from app.database import get_db
from app.models.Presupuesto import Presupuesto
from app.repositories.imp.PresupuestoRepository import PresupuestoRepository
from app.schemas.PresupuestoSchema import PresupuestoFiltros
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
    
    def obtener_pendientes_local(self):
        """
        Este lo va a usar tu API local. 
        Trae todo lo que está 'CREADO' para bajarlo al ERP de escritorio.
        """
        filtros = PresupuestoFiltros(estado="CREADO", skip=0, limit=100) # Sin paginación pesada
        return self.presupuestoRepository.get_paginado(
            skip=0, 
            limit=100, 
            estado="CREADO"
        )

    def validar_presupuesto(self, presupuesto_id: int, id_factura_local: int):
        """
        Cuando tu ERP local procesa el pedido, llama acá.
        Cambia el estado y le clava el ID de factura que generó el sistema de tu tío.
        """
        presupuesto = self.presupuestoRepository.get_by_id(presupuesto_id)
        if not presupuesto:
            raise Exception("Presupuesto no encontrado")
        
        presupuesto.estado = "VALIDADO" # type: ignore
        presupuesto.id_factura = id_factura_local # type: ignore
        
        return self.presupuestoRepository.actualizar(presupuesto)
    
    # app/services/imp/PresupuestoService.py

    def obtener_presupuestos_filtrados(self, filtros: PresupuestoFiltros, auth: dict):
        # Lógica de seguridad:
        if auth["rol"] == "client":
            # Si es cliente, forzamos que solo vea SU id_cliente de la sesión
            cliente_id_final = auth["id_cliente"]
        else:
            # Si es admin o staff, puede filtrar por el cliente que quiera
            cliente_id_final = filtros.cliente_id

        # Llamamos al repo con el ID que decidimos acá arriba
        return self.presupuestoRepository.get_paginado(
            skip=filtros.skip,
            limit=filtros.limit,
            cliente_id=cliente_id_final, 
            estado=filtros.estado,
            desde=filtros.desde,
            hasta=filtros.hasta
        )


def get_presupuesto_service(db: Any = Depends(get_db)) -> PresupuestoService:
    repository = PresupuestoRepository(db)
    return PresupuestoService(repository)