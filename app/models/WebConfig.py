from sqlalchemy import Column, Integer, String

from app.database import Base


class WebConfig(Base):
    __tablename__ = "web_config"

    id = Column(Integer, primary_key=True, index=True)
    hero_url = Column(String(255), nullable=False)
    hero_titulo = Column(String(100), nullable=True)
    hero_subtitulo = Column(String(100), nullable=True)
    
    whatsapp_contacto = Column(String(20), nullable=True)
    email_contacto = Column(String(100), nullable=True)