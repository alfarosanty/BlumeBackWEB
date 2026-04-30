from sqlalchemy.orm import Session

from app.models import SubFamilia
from app.repositories.ISubFamiliaRepository import ISubFamiliaRepository

class SubFamiliaRepository(ISubFamiliaRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_visible_subfamilias(self):
        return self.db.query(SubFamilia).filter(SubFamilia.mostrar_en_web == True).all()