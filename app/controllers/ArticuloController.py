from fastapi import APIRouter, Depends, Query, UploadFile, File
from typing import Optional, Annotated
from app.schemas.pagination import PagedResponse, PaginationParams # <--- Clase nueva
from app.services.IArticuloService import IArticuloService
from app.services.imp.ArticuloService import get_articulo_service
from app.models import Articulo, ArticuloPrecio

router = APIRouter(prefix="/articulos", tags=["Articulos"])

# Alias para la inyección del servicio (reutilizable en todo el archivo)
ArticuloServiceDep = Annotated[IArticuloService, Depends(get_articulo_service)]

@router.get("/", response_model=PagedResponse[Articulo])
def get_paginado(
    service: ArticuloServiceDep,
    pagination: Annotated[PaginationParams, Depends()], 
    codigo: Optional[str] = Query(None),
    subfamilia_id: Optional[int] = Query(None),
    articulo_precio_id: Optional[int] = Query(None)
):
    """
    Obtener artículos de forma paginada.
    """
    return service.get_paginado(
        skip=pagination.skip, 
        limit=pagination.size, 
        filtro_codigo=codigo,
        id_subfamilia=subfamilia_id,
        id_articulo_precio=articulo_precio_id
    )

@router.get("/", response_model=PagedResponse[ArticuloPrecio])
def get_precio_paginado(
    service: ArticuloServiceDep,
    pagination: Annotated[PaginationParams, Depends()], 
    codigo: Optional[str] = Query(None),
):
    """
    Obtener artículos precios de forma paginada.
    """
    return service.get_precio_paginado(
        skip=pagination.skip, 
        limit=pagination.size, 
        filtro_codigo=codigo,
    )


@router.post("/importar-precios")
def importar_precios(
    service: ArticuloServiceDep,
    file: UploadFile = File(...)
):
    return service.procesar_upsert_precios(file)

@router.post("/importar-articulos")
def importar_articulos(
    service: ArticuloServiceDep,
    file: UploadFile = File(...)
):
    return service.procesar_excel_articulos(file)