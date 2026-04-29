from pydantic import BaseModel, ConfigDict
from typing import Optional
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