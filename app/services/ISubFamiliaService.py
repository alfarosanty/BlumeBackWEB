from abc import ABC, abstractmethod
from typing import List

from app.schemas.SubfamiliaSchema import SubFamiliaSchema


class ISubFamiliaService(ABC):
    @abstractmethod
    def listar_para_web(self) -> List[SubFamiliaSchema]: pass

    @abstractmethod
    def obtener_chips_navegacion(self, sector_id: int)-> List[SubFamiliaSchema]: pass