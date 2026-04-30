from abc import ABC, abstractmethod
from typing import List
from app.models import Familia
from app.schemas.FamiliaSchema import FiltroWebDTO

class IFamiliaRepository(ABC):
    @abstractmethod
    def get_visible_familias(self) -> List[Familia]: pass

    @abstractmethod
    def get_filtros_por_sector(self, sector_id: int) -> List[FiltroWebDTO]:pass