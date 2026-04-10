from pydantic import BaseModel, ConfigDict
from typing import Optional

class ColorSchema(BaseModel):
    id: int
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    color_hexa: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)