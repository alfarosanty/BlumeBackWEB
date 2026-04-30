from typing import List

from sqlalchemy.orm import Session
from app.models import Sector
from app.repositories.ISectorRepository import ISectorRepository


class SectorRepository(ISectorRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_visible_sectores(self):
        """Trae de la base de datos solo los sectores marcados para la web."""
        return self.db.query(Sector).filter(Sector.mostrar_en_web == True).all()
    
    def get_all(self) -> List[Sector]:
        return self.db.query(Sector).all()