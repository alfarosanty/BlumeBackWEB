from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal

class ArticuloPrecioSchema(BaseModel):
    id: int
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    precio1: Decimal
    precio2: Decimal
    precio3: Decimal
    url_foto: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)