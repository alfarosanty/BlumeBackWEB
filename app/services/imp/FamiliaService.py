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
    
    def obtener_chips_navegacion(self, sector_id: int):
        # Aquí podrías ordenar alfabéticamente o por algún criterio de prioridad
        filtros = self.repo.get_filtros_por_sector(sector_id)
        return sorted(filtros, key=lambda x: x.descripcion)
    
    

