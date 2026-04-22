from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated, Optional
from app.models import Presupuesto
from app.schemas.pagination import PagedResponse, PaginationParams
from app.services.IPresupuestoService import IPresupuestoService
from app.services.imp.PresupuestoService import get_presupuesto_service


router = APIRouter(prefix="/presupuesto", tags=["Presupuesto"])

PresupuestoServiceDep = Annotated[IPresupuestoService, Depends(get_presupuesto_service)]

@router.get("/", response_model=PagedResponse[Presupuesto])
def get_paginado(
    service: PresupuestoServiceDep,
    pagination: Annotated[PaginationParams, Depends()], 
    cliente_id: Optional[int] = Query(None),
    estado: Optional[str] = Query(None),
    desde: Optional[date] = Query(None),
    hasta: Optional[date] = Query(None)
):
    """
    Obtener artículos de forma paginada.
    """
    return service.get_paginado(
        skip=pagination.skip,  # type: ignore
        limit=pagination.size, # type: ignore
        cliente_id=cliente_id,
        estado=estado,
        desde=desde,
        hasta=hasta
    )

@router.post("/", response_model=Presupuesto, status_code=status.HTTP_201_CREATED)
def crear_presupuesto(
    service: PresupuestoServiceDep,
    presupuesto: Presupuesto  # Schema para creación (sin ID)
):
    """
    Crear un nuevo presupuesto.
    """
    return service.crear(presupuesto)


@router.put("/{presupuesto_id}", response_model=Presupuesto)
def actualizar_presupuesto(
    presupuesto_id: int,
    service: PresupuestoServiceDep,
    presupuesto: Presupuesto
):
    """
    Actualizar un presupuesto existente (reemplazo total).
    """
    # Verificamos si existe antes de intentar actualizar
    db_presupuesto = service.get_by_id(presupuesto_id)
    if not db_presupuesto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Presupuesto no encontrado"
        )
        
    return service.actualizar(presupuesto)