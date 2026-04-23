from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated, Optional
from app.core.security import obtener_usuario_actual
from app.models import Presupuesto
from app.schemas.PresupuestoSchema import PresupuestoFiltros, PresupuestoResponse
from app.schemas.pagination import PagedResponse, PaginationParams
from app.services.IPresupuestoService import IPresupuestoService
from app.services.imp.PresupuestoService import get_presupuesto_service


router = APIRouter(prefix="/presupuesto", tags=["Presupuesto"])

PresupuestoServiceDep = Annotated[IPresupuestoService, Depends(get_presupuesto_service)]

@router.get("", response_model=PagedResponse[PresupuestoResponse])
def get_presupuestos(
    service: PresupuestoServiceDep,
    filtros: PresupuestoFiltros = Depends(),
    auth: dict = Depends(obtener_usuario_actual)
):
    return service.obtener_presupuestos_filtrados(filtros, auth)

@router.post("/", response_model=PresupuestoResponse, status_code=status.HTTP_201_CREATED)
def crear_presupuesto(
    service: PresupuestoServiceDep,
    presupuesto: Presupuesto,  # Tu modelo/schema completo
    auth: dict = Depends(obtener_usuario_actual)
):
    if auth["rol"] == "client" and presupuesto.id_cliente != auth["id_cliente"]:
        raise HTTPException(status_code=403, detail="No podés crear presupuestos para otro cliente")
        
    return service.crear(presupuesto)

@router.put("/{presupuesto_id}", response_model=PresupuestoResponse)
def actualizar_presupuesto(
    presupuesto_id: int,
    service: PresupuestoServiceDep,
    presupuesto: Presupuesto,
    auth: dict = Depends(obtener_usuario_actual)
):
    db_presupuesto = service.get_by_id(presupuesto_id)
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    if auth["rol"] == "client" and db_presupuesto.id_cliente != auth["id_cliente"]:
        raise HTTPException(status_code=403, detail="No tenés permiso para editar este presupuesto")

    presupuesto.id = presupuesto_id # type: ignore
    return service.actualizar(presupuesto)