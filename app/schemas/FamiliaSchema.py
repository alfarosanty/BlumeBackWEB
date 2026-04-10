from pydantic import BaseModel, ConfigDict
from typing import Optional

class FamiliaSchema(BaseModel):
    id: int
    codigo: Optional[str] = None
    descripcion: str

    model_config = ConfigDict(from_attributes=True)