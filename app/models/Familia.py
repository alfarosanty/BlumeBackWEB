from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Familia(Base):
    __tablename__ = "familias"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=True)
    descripcion = Column(String(100), nullable=False)
    id_sector = Column(Integer, ForeignKey("sector.id"), nullable=True)
    mostrar_en_web = Column(Boolean, default=False)

    # Relación hacia abajo: Una familia tiene muchas subfamilias
    subfamilias = relationship("SubFamilia", back_populates="familia")
    sector = relationship("Sector", back_populates="familias")
