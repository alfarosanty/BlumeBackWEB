import cloudinary.uploader
from fastapi.concurrency import run_in_threadpool
from app.schemas import SectorSchema
from app.services.ISectorService import ISectorService
from app.repositories.imp.SectorRepository import SectorRepository
from sqlalchemy.orm import Session

FOLDER_SECTORES = "blume/sectores"

class SectorService(ISectorService):
    def __init__(self, repo: SectorRepository):
        self.repo = repo

    def listar_sectores_para_ecommerce(self):
        sectores_db = self.repo.get_visible_sectores()
        return [SectorSchema.model_validate(s) for s in sectores_db]
    
    async def update_sector(self, db: Session, sector_id: int, **kwargs):
        db_sector = self.repo.get_by_id(sector_id) 
        
        if not db_sector:
            raise Exception(f"No se encontró el sector con ID {sector_id}")

        archivo = kwargs.get('archivo_foto')
        if archivo:
            try:
                upload_result = await run_in_threadpool(
                    cloudinary.uploader.upload,
                    archivo.file,
                    folder=FOLDER_SECTORES,
                    public_id=f"sector_{sector_id}", 
                    overwrite=True
                )
                db_sector.url_foto = upload_result["secure_url"] 

            except Exception as e:
                print(f"Error Cloudinary Sector: {e}")
                raise Exception("Error al procesar la imagen del sector")

        if kwargs.get('nombre'):
            db_sector.nombre = kwargs.get('nombre')
        if kwargs.get('descripcion'):
            db_sector.descripcion = kwargs.get('descripcion') # type: ignore
            setattr(db_sector, 'descripcion', kwargs.get('descripcion'))

        return self.repo.update(db_sector)