from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class PresupuestoFiltros(BaseModel):
    skip: int = 0
    limit: int = 10
    cliente_id: Optional[int] = None
    estado: Optional[str] = None
    desde: Optional[datetime] = None
    hasta: Optional[datetime] = None

# Este es el que usás en el response_model del Controller
class PresupuestoResponse(BaseModel):
    id: int
    fecha_creacion: datetime
    id_cliente: int
    estado: str
    total: float
    id_factura: Optional[int] = None
    # cliente: Optional[ClienteResponse] # Si querés devolver datos del cliente
    
    class Config:
        from_attributes = True # Esto es CLAVE para que funcione con SQLAlchemy