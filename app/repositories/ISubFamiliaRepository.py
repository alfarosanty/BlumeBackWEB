from abc import ABC, abstractmethod
from typing import List
from app.models import SubFamilia
from app.schemas.FamiliaSchema import FiltroWebDTO

class ISubFamiliaRepository(ABC):
    @abstractmethod
    def get_visible_subfamilias(self) -> List[SubFamilia]: pass
