
from datetime import datetime
from typing import Any
from fastapi import Depends, HTTPException, status
from app.database import get_db
from app.models import ArticuloPresupuesto, EstadoPresupuesto
from app.models.Presupuesto import Presupuesto
from app.models.Usuario import Usuario
from app.repositories.imp.PresupuestoRepository import PresupuestoRepository
from app.schemas.PresupuestoSchema import PresupuestoCreate, PresupuestoFiltros, PresupuestoUpdate
from app.repositories.IPresupuestoRepository import IPresupuestoRepository
from app.services.IPresupuestoService import IPresupuestoService
import time


class PresupuestoService(IPresupuestoService):
    presupuestoRepository: IPresupuestoRepository

    def __init__(self, presupuestoRepository: IPresupuestoRepository):
        self.presupuestoRepository = presupuestoRepository
    
    def obtener_presupuestos_filtrados(self, filtros: PresupuestoFiltros, auth: Usuario):
        if auth.rol == "client": # type: ignore
            cliente_id_final = auth.id_cliente
        else:
            cliente_id_final = filtros.cliente_id

        return self.presupuestoRepository.get_paginado(
            skip=filtros.skip,
            limit=filtros.limit,
            cliente_id=cliente_id_final, 
            estado=filtros.estado,
            desde=filtros.desde,
            hasta=filtros.hasta
        )
    
    def crear(self, presupuesto: PresupuestoCreate):
        
        # 1. Validaciones
        if not presupuesto.id_cliente:
            raise HTTPException(status_code=400, detail="Falta id_cliente")
        if not presupuesto.articulos:
            raise HTTPException(status_code=400, detail="Presupuesto vacío")

        db_presupuesto = Presupuesto(
            id_cliente=presupuesto.id_cliente,
            estado=EstadoPresupuesto.CREADO,
            fecha_creacion=datetime.now(),
            total=0
        )

        total_acumulado = 0
        
        for i, item in enumerate(presupuesto.articulos):
            faltantes = []
            if not item.id_articulo: faltantes.append("id_articulo")
            if not item.codigo: faltantes.append("codigo")
            if not item.descripcion: faltantes.append("descripcion")
            if not item.cantidad or item.cantidad <= 0: faltantes.append("cantidad (mayor a 0)")
            if item.precio_unitario is None: faltantes.append("precio_unitario")

            if faltantes:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Error en el artículo pos {i}: Faltan o son inválidos: {', '.join(faltantes)}"
                )

            nuevo_articulo = ArticuloPresupuesto(
                id_articulo=item.id_articulo,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                descripcion=item.descripcion,
                codigo=item.codigo,
                fecha_creacion=datetime.now()
            )
            total_acumulado += (item.cantidad * item.precio_unitario)
            db_presupuesto.articulos.append(nuevo_articulo)


        db_presupuesto.total = total_acumulado  # type: ignore

        try:
            resultado = self.presupuestoRepository.crear(db_presupuesto)
            
            return resultado
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_by_id(self, presupuesto_id: int):
        return self.presupuestoRepository.get_by_id(presupuesto_id)
    
    def actualizar(self, presupuesto_id: int, presupuesto_in: PresupuestoUpdate) -> Presupuesto:
        db_presupuesto = self.presupuestoRepository.get_by_id(presupuesto_id)
        if not db_presupuesto:
            raise ValueError("Presupuesto no encontrado")

        update_data = presupuesto_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_presupuesto, field, value)

        return self.presupuestoRepository.actualizar(db_presupuesto)
    
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



def get_presupuesto_service(db: Any = Depends(get_db)) -> PresupuestoService:
    repository = PresupuestoRepository(db)
    return PresupuestoService(repository)