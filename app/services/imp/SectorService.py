from app.schemas import SectorSchema
from app.services.ISectorService import ISectorService
from app.repositories.imp.SectorRepository import SectorRepository


class SectorService(ISectorService):
    def __init__(self, repo: SectorRepository):
        self.repo = repo

    def listar_sectores_para_ecommerce(self):
        sectores_db = self.repo.get_visible_sectores()
        
        return [SectorSchema.model_validate(s) for s in sectores_db]