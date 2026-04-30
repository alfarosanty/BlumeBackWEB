from abc import ABC, abstractmethod
from typing import List

from app.schemas import FamiliaSchema, FiltroWebDTO


class IFamiliaService(ABC):
    @abstractmethod
    def listar_para_web(self)-> List[FamiliaSchema]: pass

    @abstractmethod
    def obtener_chips_navegacion(self, sector_id: int)-> List[FiltroWebDTO]: pass