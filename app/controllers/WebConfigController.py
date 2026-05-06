from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import WebConfigSchema
from app.services.imp.WebConfigService import WebConfigService

router = APIRouter(prefix="/config", tags=["Configuración"])

@router.get("/home")
def get_home_config(db: Session = Depends(get_db)):
    return WebConfigService.get_home_config(db)

@router.put("/update/1")
async def update_web_config(
    hero_titulo: Optional[str] = Form(None),
    hero_subtitulo: Optional[str] = Form(None),
    whatsapp_contacto: Optional[str] = Form(None),
    email_contacto: Optional[str] = Form(None),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        return await WebConfigService.update_config(
            db, 
            config_id=1,
            titulo=hero_titulo,
            subtitulo=hero_subtitulo,
            wsp=whatsapp_contacto,
            email=email_contacto,
            archivo_foto=foto
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))