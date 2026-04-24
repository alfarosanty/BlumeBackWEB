from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

from app.models import EstadoPresupuesto
from app.schemas import ArticuloSchema

class PresupuestoFiltros(BaseModel):
    skip: int = 0
    limit: int = 10
    cliente_id: Optional[int] = None
    estado: Optional[str] = None
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None
    

class ArticuloPresupuestoCreate(BaseModel):
    id_articulo: int
    cantidad: int
    precio_unitario: float
    descripcion: Optional[str] = None
    codigo: Optional[str] = None

class PresupuestoCreate(BaseModel):
    id_cliente: int
    articulos: List[ArticuloPresupuestoCreate] 

class PresupuestoUpdate(BaseModel):
    id_cliente: Optional[int] = None
    estado: Optional[EstadoPresupuesto] = None
    total: Optional[float] = None

    class Config:
        from_attributes = True # Esto es CLAVE para que funcione con SQLAlchemy

class ArticuloPresupuestoResponse(BaseModel):
    id: int
    id_articulo: int
    cantidad: int
    precio_unitario: float
    articulo: ArticuloSchema
    codigo: str
    descripcion: str
    
    model_config = ConfigDict(from_attributes=True)

class PresupuestoResponse(BaseModel):
    id: int
    fecha_creacion: datetime
    id_cliente: int
    estado: str
    total: float
    articulos: List[ArticuloPresupuestoResponse]
    
    model_config = ConfigDict(from_attributes=True)