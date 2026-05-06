from typing import List

from app.repositories.IFamiliaRepository import IFamiliaRepository
from app.schemas import FamiliaSchema
from app.services.IFamiliaService import IFamiliaService


class FamiliaService(IFamiliaService):
    def __init__(self, repo: IFamiliaRepository):
        self.repo = repo

    def listar_para_web(self) -> List[FamiliaSchema]:

        familias_db = self.repo.get_visible_familias()


        return  [FamiliaSchema.model_validate(s) for s in familias_db]
    
    def obtener_chips_navegacion(self, sector_id: int) -> List[FamiliaSchema]:
        familias_db = self.repo.get_familia_por_sector(sector_id)

        familias_validadas = [
            FamiliaSchema.model_validate(f) for f in familias_db
        ]

        return sorted(familias_validadas, key=lambda x: x.descripcion.lower())
    
    

