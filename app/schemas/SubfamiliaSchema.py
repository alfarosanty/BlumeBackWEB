from pydantic import BaseModel, ConfigDict
from typing import Optional

from app.schemas.FamiliaSchema import FamiliaSchema


class SubFamiliaSchema(BaseModel):
    id: int
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    id_familia: Optional[int] = None
    
    # Anidamos el objeto Familia completo
    familia: Optional[FamiliaSchema] = None

    model_config = ConfigDict(from_attributes=True)