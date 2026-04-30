from abc import ABC, abstractmethod
from typing import List

from app.schemas.SubfamiliaSchema import SubFamiliaSchema


class ISubFamiliaService(ABC):
    @abstractmethod
    def listar_para_web(self) -> List[SubFamiliaSchema]: pass