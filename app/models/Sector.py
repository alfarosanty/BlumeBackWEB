from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Sector(Base):
    __tablename__ = "sector"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=True)
    descripcion = Column(String(100), nullable=False)

    # Relación: Un sector tiene muchas familias
    familias = relationship("Familia", back_populates="sector")