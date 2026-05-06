from pydantic import BaseModel, EmailStr
from typing import Optional

class WebConfigSchema(BaseModel):
    id: Optional[int] = None
    hero_url: str
    hero_titulo: Optional[str] = None
    hero_subtitulo: Optional[str] = None
    whatsapp_contacto: Optional[str] = None
    email_contacto: Optional[str] = None

class WebConfigUpdate(BaseModel):
    hero_titulo: Optional[str] = None
    hero_subtitulo: Optional[str] = None
    whatsapp_contacto: Optional[str] = None
    email_contacto: Optional[EmailStr] = None

    class Config:
        from_attributes = True