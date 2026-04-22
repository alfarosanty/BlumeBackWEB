from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional

from app.models import Cliente
from app.schemas.pagination import PagedResponse, PaginationParams
from app.services.IClienteService import IClienteService
from app.services.imp.ClienteService import get_cliente_service


router = APIRouter(prefix="/Cliente", tags=["Cliente"])

ClienteServiceDep = Annotated[IClienteService, Depends(get_cliente_service)]

@router.get("/", response_model=PagedResponse[Cliente])
def get_paginado(
    service: ClienteServiceDep,
    pagination: Annotated[PaginationParams, Depends()], 
    id: Optional[int] = Query(None),
):
    """
    Obtener clientes de forma paginada.
    """
    return service.get_paginado(
        skip=pagination.skip,  # type: ignore
        limit=pagination.size, # type: ignore
        id=id
    )

#@router.post("/", response_model=Cliente)
#def crear(
#    service: ClienteServiceDep,
#    cliente: Cliente # Recibís un diccionario genérico en vez de un modelo
#):
#    return service.crear(cliente.razon_social, cliente.cuit, cliente.telefono)

@router.put("/{cliente_id}", response_model=Cliente)
def actualizar(
    service: ClienteServiceDep,
    cliente: Cliente
):
    """
    Actualizar un cliente existente por su ID.
    """
    return service.actualizar(cliente)