from abc import ABC, abstractmethod
from typing import Any, Optional


from app.models import ArticuloMaestro

class IArticuloMaestroService(ABC):
    @abstractmethod
    def subir_maestros_desde_excel(self, file: Any) -> int:
        pass

    @abstractmethod
    def obtener_todos(self, solo_activos: bool, skip: Optional[int] = 0, limit: Optional[int] = 20) -> list[ArticuloMaestro]:
        pass