from pydantic import BaseModel, Field
from typing import List, Generic, Optional, TypeVar, Type

# Definimos un tipo genérico T (como en C#)
T = TypeVar("T")

class PagedResponse(BaseModel, Generic[T]):
    items: List[T]
    total_registros: int
    pagina_actual: int
    paginas_totales: int
    limite_por_pagina: int

    @classmethod
    def crear(cls, items: List[T], total: int, skip: int, limit: int):
        import math
        return cls(
            items=items,
            total_registros=total,
            pagina_actual=(skip // limit) + 1,
            paginas_totales=math.ceil(total / limit) if limit > 0 else 1,
            limite_por_pagina=limit
        )
    

class PaginationParams(BaseModel):
    # Al ponerle None, FastAPI entiende que son opcionales
    pagina: Optional[int] = Field(None, ge=1, description="Número de página")
    size: Optional[int] = Field(None, ge=1, le=100, description="Registros por página")

    @property
    def skip(self) -> Optional[int]:
        if self.pagina is None or self.size is None:
            return None
        return (self.pagina - 1) * self.size