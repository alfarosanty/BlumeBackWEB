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
