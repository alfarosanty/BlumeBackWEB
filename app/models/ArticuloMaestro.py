from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Mapped, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.ArticuloPrecio import ArticuloPrecio

class ArticuloMaestro(Base):
    __tablename__ = 'ArticuloMaestro'
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), nullable=True)
    descripcion = Column(String(100), nullable=True)
    url_foto = Column(String(200), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)  # <-- Nueva columna agregada

    variantes: Mapped[List["ArticuloPrecio"]] = relationship(
        secondary="ArticuloMaestroXArticuloPrecio", 
        back_populates="maestros"
    )