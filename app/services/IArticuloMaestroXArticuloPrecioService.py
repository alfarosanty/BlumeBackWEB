from abc import ABC, abstractmethod
from typing import Any

class IArticuloMaestroXArticuloPrecioService(ABC):
    @abstractmethod
    def vincular_articulos_por_ids(self, file: Any) -> int:
        pass