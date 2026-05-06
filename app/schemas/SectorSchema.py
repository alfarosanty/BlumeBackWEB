from typing import Optional

from pydantic import BaseModel

class SectorSchema(BaseModel):
    id: int
    descripcion: str
    codigo: str
    mostrar_en_web: bool
    url_foto: Optional[str] = None

    class Config:
        from_attributes = True