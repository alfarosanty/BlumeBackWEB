from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class SubFamilia(Base):
    __tablename__ = "subfamilias"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), nullable=True)
    descripcion = Column(String(100), nullable=True)
    id_familia = Column(Integer, ForeignKey("familias.id"), nullable=True)
    mostrar_en_web = Column(Boolean, default=False)

    familia = relationship("Familia", back_populates="subfamilias")
    articulos = relationship("Articulo", back_populates="subfamilia")