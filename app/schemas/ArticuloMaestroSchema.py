from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class MedidaDto(BaseModel):
    id: int
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class SectorDto(BaseModel):
    id: int
    codigo: str
    descripcion: str
    model_config = ConfigDict(from_attributes=True)


class FamiliaConSectorDto(BaseModel):
    id: int
    descripcion: str
    sector: Optional[SectorDto] = None
    model_config = ConfigDict(from_attributes=True)


class SubFamiliaConJerarquiaDto(BaseModel):
    id: int
    descripcion: str
    familia: Optional[FamiliaConSectorDto] = None
    model_config = ConfigDict(from_attributes=True)


class ArticuloPrecioConMedidaDto(BaseModel):
    id: int
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    precio1: float = 0.0
    precio2: float = 0.0
    precio3: float = 0.0
    habilitado: bool
    medida: Optional[MedidaDto] = None


class ArticuloMaestroDto(BaseModel):
    id: int
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    url_foto: Optional[str] = None
    activo: bool
    subfamilia: Optional[SubFamiliaConJerarquiaDto] = None
    variantes: List[ArticuloPrecioConMedidaDto] = []
