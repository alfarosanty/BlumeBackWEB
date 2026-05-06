from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from app.models import Sector
from app.schemas import SectorSchema


class ISectorService(ABC):
    @abstractmethod
    def listar_sectores_para_ecommerce(self) -> List[SectorSchema]:
        pass

    @abstractmethod
    async def update_sector(self, db: Session, sector_id: int, **kwargs) -> Sector:
        pass