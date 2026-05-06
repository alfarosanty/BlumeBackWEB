from typing import List

from sqlalchemy.orm import Session
from app.models import Sector
from app.repositories.ISectorRepository import ISectorRepository


class SectorRepository(ISectorRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_visible_sectores(self):
        return self.db.query(Sector).filter(Sector.mostrar_en_web == True).all()

    def get_by_id(self, sector_id: int):
        return self.db.query(Sector).filter(Sector.id == sector_id).first()

    def update(self, entity: Sector):
        self.db.commit()
        self.db.refresh(entity)
        return entity