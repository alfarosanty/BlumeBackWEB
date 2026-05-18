from typing import List

from sqlalchemy import Boolean, Column, Integer, String, Numeric
from sqlalchemy.orm import Mapped, relationship
from app.database import Base
from app.models.ArticuloMaestro import ArticuloMaestro

class ArticuloPrecio(Base):
    __tablename__ = "articulos_precio"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), nullable=True)
    descripcion = Column(String(255), nullable=True)
    precio1 = Column(Numeric(10, 2), default=0.0)
    precio2 = Column(Numeric(10, 2), default=0.0)
    precio3 = Column(Numeric(10, 2), default=0.0)
    habilitado = Column(Boolean, default=True)

    maestros: Mapped[List["ArticuloMaestro"]] = relationship(
        secondary="ArticuloMaestroXArticuloPrecio", 
        back_populates="variantes"
    )
