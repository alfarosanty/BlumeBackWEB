from pydantic import BaseModel

class SectorSchema(BaseModel):
    id: int
    descripcion: str
    codigo: str
    mostrar_en_web: bool

    class Config:
        from_attributes = True