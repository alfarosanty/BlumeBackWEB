from abc import ABC, abstractmethod
from typing import List
from app.models import Sector
from sqlalchemy.orm import Session

class ISectorRepository(ABC):
    @abstractmethod
    def get_visible_sectores(self) -> List[Sector]: pass

    @abstractmethod
    def get_by_id(self, sector_id: int) -> Sector: pass

    @abstractmethod
    def update(self, entity: Sector) -> Sector: pass