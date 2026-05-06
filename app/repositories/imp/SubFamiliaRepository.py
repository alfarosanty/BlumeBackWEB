from typing import List

from sqlalchemy.orm import Session

from app.models import Familia, SubFamilia
from app.repositories.ISubFamiliaRepository import ISubFamiliaRepository

class SubFamiliaRepository(ISubFamiliaRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_visible_subfamilias(self):
        return self.db.query(SubFamilia).filter(SubFamilia.mostrar_en_web == True).all()
    
    def get_subfamilia_por_sector(self, sector_id: int) -> List[SubFamilia]:
        subfamilias = self.db.query(SubFamilia).join(Familia).filter(
            Familia.id_sector == sector_id,
            SubFamilia.mostrar_en_web == True
        ).all()

        return subfamilias