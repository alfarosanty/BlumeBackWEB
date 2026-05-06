from typing import List

from app.repositories.ISubFamiliaRepository import ISubFamiliaRepository
from app.schemas.SubfamiliaSchema import SubFamiliaSchema
from app.services.ISubFamiliaService import ISubFamiliaService


class SubFamiliaService(ISubFamiliaService):
    def __init__(self, repo: ISubFamiliaRepository):
        self.repo = repo

    def listar_para_web(self) -> List[SubFamiliaSchema]:

        subfamilias_db = self.repo.get_visible_subfamilias()


        return  [SubFamiliaSchema.model_validate(s) for s in subfamilias_db]
    
    def obtener_chips_navegacion(self, sector_id: int) -> list[SubFamiliaSchema]:
        filtros = self.repo.get_subfamilia_por_sector(sector_id)

        filtros_schema = [SubFamiliaSchema.model_validate(f) for f in filtros]
        
        return sorted(filtros_schema, key=lambda x: x.descripcion or "")
