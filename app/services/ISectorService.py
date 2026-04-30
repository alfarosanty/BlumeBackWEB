from abc import ABC, abstractmethod
from typing import List

from app.schemas import SectorSchema


class ISectorService(ABC):
    @abstractmethod
    def listar_sectores_para_ecommerce(self) -> List[SectorSchema]:
        """Lógica para filtrar y devolver sectores visibles"""
        pass