from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from typing import List, Optional, Annotated, Dict
from sqlalchemy.orm import Session

from app.database import get_db  # Ajustá la ruta según dónde tengas tu get_db
from app.models.Usuario import Usuario
from app.services.IArticuloService import IArticuloService
from app.services.imp.ArticuloService import get_articulo_service

from app.schemas import PagedResponse, PaginationParams, ArticuloSchema, ArticuloPrecioSchema, ArticuloSugerencia, ArticuloMaestroResponse
from app.core.security import obtener_usuario_confirmado, verificar_rol

router = APIRouter(prefix="/articulos", tags=["Articulos"])

# Alias para la inyección del servicio (reutilizable en todo el archivo)
ArticuloServiceDep = Annotated[IArticuloService, Depends(get_articulo_service)]

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
    


@router.get("/maestro", response_model=PagedResponse[ArticuloMaestroResponse])
async def get_todos_los_maestros(
    service: ArticuloServiceDep,
    pagination: Annotated[PaginationParams, Depends()],
    solo_activos: bool = Query(True, description="Si es True, trae solo los maestros activos. Si es False, trae todos."),
    codigo: Optional[str] = Query(None, description="Filtra por código del ArticuloMaestro"),
    subfamilia_id: Optional[int] = Query(None, description="Filtra maestros que tengan al menos un artículo de esta subfamilia"),
    familia_id: Optional[int] = Query(None, description="Filtra maestros que tengan al menos un artículo de esta familia"),
    sector_id: Optional[int] = Query(None, description="Filtra maestros que tengan al menos un artículo de este sector"),
    auth: Usuario = Depends(obtener_usuario_confirmado)
):
    """
    Obtiene los artículos maestro de la base de datos con filtro opcional por estado activo y paginación.
    """
    return service.obtener_maestros_paginado(
        solo_activos=solo_activos,
        skip=pagination.skip or 0,
        limit=pagination.size or 20,
        filtro_codigo=codigo,
        id_subfamilia=subfamilia_id,
        id_familia=familia_id,
        id_sector=sector_id
    )
