from fastapi import APIRouter, Depends, Query, UploadFile, File
from typing import List, Optional, Annotated
from app.models.Usuario import Usuario
from app.services.IArticuloService import IArticuloService
from app.services.imp.ArticuloService import get_articulo_service
from app.schemas import PagedResponse, PaginationParams, ArticuloSchema, ArticuloPrecioSchema, ArticuloSugerencia

from app.core.security import verificar_rol

router = APIRouter(prefix="/articulos", tags=["Articulos"])

# Alias para la inyección del servicio (reutilizable en todo el archivo)
ArticuloServiceDep = Annotated[IArticuloService, Depends(get_articulo_service)]


@router.get("", response_model=PagedResponse[ArticuloSchema])
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

@router.get("/precios", response_model=PagedResponse[ArticuloPrecioSchema])
def get_precio_paginado(
    service: ArticuloServiceDep,
    pagination: Annotated[PaginationParams, Depends()], 
    codigo: Optional[str] = Query(None),
):
    # Aquí pasamos los valores tal cual, podrían ser None
    return service.get_precio_paginado(
        skip=pagination.skip, 
        limit=pagination.size, 
        filtro_codigo=codigo,
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
    q: Annotated[str, Query(min_length=2, description="Texto a buscar en código o descripción")]
):
    """
    Búsqueda rápida y 'fuzzy' para sugerencias en vivo (Lupita).
    Retorna los 5 mejores resultados usando Full-Text Search + Stemming.
    """
    return service.get_sugerencias(query_usuario=q)