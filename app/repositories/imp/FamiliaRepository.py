from typing import List

from sqlalchemy.orm import Session
from app.models import Familia, SubFamilia
from app.repositories.IFamiliaRepository import IFamiliaRepository
from app.schemas.FamiliaSchema import FiltroWebDTO

class FamiliaRepository(IFamiliaRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_visible_familias(self):
        return self.db.query(Familia).filter(Familia.mostrar_en_web == True).all()

    def get_filtros_por_sector(self, sector_id: int) -> List[FiltroWebDTO]:
        familias = self.db.query(Familia).filter(
            Familia.id_sector == sector_id,
            Familia.mostrar_en_web == True
        ).all()


        subfamilias = self.db.query(SubFamilia).join(Familia).filter(
            Familia.id_sector == sector_id,
            SubFamilia.mostrar_en_web == True
        ).all()

        resultado = []
        
        for f in familias:
            resultado.append(FiltroWebDTO(id=f.id, descripcion=f.descripcion, tipo="familia")) # type: ignore
            
        for sf in subfamilias:
            resultado.append(FiltroWebDTO(id=sf.id, descripcion=sf.descripcion, tipo="subfamilia")) # type: ignore

        return resultado