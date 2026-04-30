from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.SectorSchema import SectorSchema

class FamiliaSchema(BaseModel):
    id: int
    codigo: Optional[str] = None
    descripcion: str
    id_sector: Optional[int] = None
    
    sector: Optional[SectorSchema] = None

    model_config = ConfigDict(from_attributes=True)

class FiltroWebDTO(BaseModel):
    id: int
    descripcion: str
    tipo: str