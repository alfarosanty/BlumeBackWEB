import cloudinary.uploader
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.repositories.imp.WebConfigRepository import WebConfigRepository

FOLDER_CONFIG = "blume/web_config"

class WebConfigService:
    @staticmethod
    def get_home_config(db: Session):
        config = WebConfigRepository.get_config(db)
        
        if not config:
            return {
                "hero_url": "v12345/default-hero.jpg",
                "hero_titulo": "Blume",
                "hero_subtitulo": "Textiles de Diseño"
            }
        return config
    
    @staticmethod
    async def update_config(db: Session, config_id: int, **kwargs):
        db_config = WebConfigRepository.get_by_id(db, config_id)
        if not db_config:
            raise Exception("No se encontró la configuración")

        archivo = kwargs.get('archivo_foto')
        if archivo:
            try:
                upload_result = await run_in_threadpool(
                    cloudinary.uploader.upload,
                    archivo.file,
                    folder=FOLDER_CONFIG,
                    public_id="hero_home_principal",
                    overwrite=True
                )
                db_config.hero_url = upload_result["secure_url"] 
                
            except Exception as e:
                print(f"Error en Cloudinary: {e}")
                raise Exception("Error al procesar la imagen") 

        # MAPEADO DE TEXTOS
        mapeo = {
            "titulo": "hero_titulo",
            "subtitulo": "hero_subtitulo",
            "wsp": "whatsapp_contacto",
            "email": "email_contacto"
        }

        for clave_arg, columna in mapeo.items():
            valor = kwargs.get(clave_arg)
            if valor is not None:
                setattr(db_config, columna, valor)

        return WebConfigRepository.update(db, db_config)