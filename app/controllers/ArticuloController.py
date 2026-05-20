from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from typing import List, Optional, Annotated, Dict
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Usuario import Usuario
from app.services.IArticuloService import IArticuloService
from app.services.imp.ArticuloService import get_articulo_service
from app.services.IArticuloMaestroService import IArticuloMaestroService
from app.services.imp.ArticuloMaestroService import get_articulo_maestro_service

from app.schemas import PagedResponse, PaginationParams, ArticuloSchema, ArticuloPrecioSchema, ArticuloSugerencia
from app.schemas.ApiResponseSchema import ApiResponse, PagedResult
from app.schemas.ArticuloMaestroSchema import ArticuloMaestroDto
from app.core.security import obtener_usuario_confirmado, verificar_rol

router = APIRouter(prefix="/articulos", tags=["Articulos"])

ArticuloServiceDep = Annotated[IArticuloService, Depends(get_articulo_service)]
ArticuloMaestroServiceDep = Annotated[IArticuloMaestroService, Depends(get_articulo_maestro_service)]

@router.get("", response_model=PagedResponse[ArticuloSchema])
def get_paginado(
    service: ArticuloServiceDep,
    pagination: Annotated[PaginationParams, Depends()], 
    codigo: Optional[str] = Query(None),
    subfamilia_id: Optional[int] = Query(None),
    articulo_precio_id: Optional[int] = Query(None),
    auth: Usuario = Depends(obtener_usuario_confirmado)
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

@router.get("/precios", response_model=PagedResponse[ArticuloPrecioSchema])
def get_precio_paginado(
    service: ArticuloServiceDep,
    pagination: Annotated[PaginationParams, Depends()], 
    codigo: Optional[str] = Query(None),
    sector_id: Optional[int] = Query(None),
    familia_id: Optional[int] = Query(None),
    subfamilia_id: Optional[int] = Query(None), # Filtro por subfamilia del ArticuloPrecio
    codigo_maestro: Optional[str] = Query(None, description="Filtra por código del ArticuloMaestro asociado"),
    auth: Usuario = Depends(obtener_usuario_confirmado)
):
    return service.get_precio_paginado(
        skip=pagination.skip or 0, 
        limit=pagination.size or 20, 
        filtro_codigo=codigo,
        sector_id=sector_id,
        familia_id=familia_id,
        subfamilia_id=subfamilia_id,
        filtro_codigo_maestro=codigo_maestro
    )


@router.post("/importar-precios")
def importar_precios(
    service: ArticuloServiceDep,
    file: UploadFile = File(...),
    usuario: Usuario = Depends(verificar_rol(["super_admin", "staff"]))
):
    return service.procesar_upsert_precios(file)

@router.post("/importar-articulos")
def importar_articulos(
    service: ArticuloServiceDep,
    file: UploadFile = File(...),
    usuario: Usuario = Depends(verificar_rol(["super_admin", "staff"]))
):
    return service.procesar_excel_articulos(file)

@router.post("/{articulo_precio_id}/foto")
async def subir_foto_articulo(
    articulo_precio_id: int,
    service: ArticuloServiceDep,
    file: UploadFile = File(...),
    usuario: Usuario = Depends(verificar_rol(["super_admin", "staff"]))
):
    """
    Sube una foto a Cloudinary y asocia la URL al artículo en la base de datos.
    """
    if file.content_type is None or not file.content_type.startswith("image/"):
            return {"error": "El archivo no es una imagen válida"}
    
    return await service.subir_foto(articulo_precio_id, file)

@router.get("/sugerencias", response_model=List[ArticuloSugerencia])
def get_sugerencias(
    service: ArticuloServiceDep,
    q: Annotated[str, Query(min_length=2, description="Texto a buscar en código o descripción")],
    auth: Usuario = Depends(obtener_usuario_confirmado)
):
    """
    Búsqueda rápida y 'fuzzy' para sugerencias en vivo (Lupita).
    Retorna los 5 mejores resultados usando Full-Text Search + Stemming.
    """
    return service.get_sugerencias(query_usuario=q)

@router.post("/articulo-maestro/cargar", response_model=Dict)
async def cargar_maestros(
    service: ArticuloServiceDep,
    file: UploadFile = File(...), 
    usuario: Usuario = Depends(verificar_rol(["super_admin", "staff"]))
):
    try:
        cantidad = service.subir_maestros_desde_excel(file.file)
        
        return {
            "mensaje": "Carga de maestros exitosa",
            "registros_procesados": cantidad
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar maestros: {str(e)}")

@router.post("/maestro/vincular-precios", response_model=Dict)
async def vincular_precios(
    service: ArticuloServiceDep,
    file: UploadFile = File(...), 
    usuario: Usuario = Depends(verificar_rol(["super_admin", "staff"]))
):
    try:
        cantidad = service.vincular_maestros_precios_excel(file.file)
        
        return {
            "mensaje": "Vinculación de precios completada",
            "relaciones_creadas": cantidad
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la vinculación: {str(e)}")
    


@router.get("/maestro", response_model=ApiResponse[PagedResult[ArticuloMaestroDto]])
async def get_maestros_paginado(
    service: ArticuloMaestroServiceDep,
    auth: Usuario = Depends(obtener_usuario_confirmado),
    pageNumber: int = Query(default=1, ge=1, description="Número de página (desde 1)"),
    pageSize: int = Query(default=20, ge=1, le=100, description="Registros por página (máx 100)"),
    activo: Optional[bool] = Query(default=None, description="True → solo activos; omitido o False → todos"),
    codigo: Optional[str] = Query(default=None, description="Filtra por código (contiene, case-insensitive)"),
    sectorId: Optional[int] = Query(default=None, description="Filtra por Sector"),
    familiaId: Optional[int] = Query(default=None, description="Filtra por Familia"),
    subfamiliaId: Optional[int] = Query(default=None, description="Filtra por SubFamilia"),
):
    """Retorna artículos maestro paginados con su jerarquía de categorías y variantes de precio."""
    total, items = service.obtener_paginado(
        solo_activos=activo,
        codigo=codigo,
        sector_id=sectorId,
        familia_id=familiaId,
        subfamilia_id=subfamiliaId,
        page_number=pageNumber,
        page_size=pageSize,
    )
    return ApiResponse.ok(
        PagedResult.crear(items=items, total=total, page_number=pageNumber, page_size=pageSize)
    )
