from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from .ColorSchema import ColorSchema
from .MedidaSchema import MedidaSchema
from .SubfamiliaSchema import SubFamiliaSchema
from .ArticuloPrecioSchema import ArticuloPrecioSchema

class ArticuloSchema(BaseModel):
    id: int
    codigo: str
    descripcion: str
    habilitado: bool
    
    # IDs (por si el frontend los necesita sueltos)
    id_color: Optional[int] = None
    id_medida: Optional[int] = None
    id_subfamilia: Optional[int] = None
    id_articulo_precio: Optional[int] = None
    
    # Objetos Anidados (La "magia" para el Frontend)
    color: Optional[ColorSchema] = None
    medida: Optional[MedidaSchema] = None
    subfamilia: Optional[SubFamiliaSchema] = None
    articulo_precio: Optional[ArticuloPrecioSchema] = None

    model_config = ConfigDict(from_attributes=True)

class ArticuloSugerencia(BaseModel):
    id: int
    codigo: str
    descripcion: str
    url_foto: Optional[str] = None
    precio: Optional[float] = None

    class Config:
        from_attributes = True

class VariantePrecioSchema(BaseModel):
    id: int
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    precio1: float = 0.0
    habilitado: bool
    subfamilia: SubFamiliaSchema

    class Config:
        from_attributes = True

class ArticuloMaestroResponse(BaseModel):
    id: int
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    url_foto: Optional[str] = None
    activo: bool
    variantes: List[VariantePrecioSchema] = []

    class Config:
        from_attributes = True