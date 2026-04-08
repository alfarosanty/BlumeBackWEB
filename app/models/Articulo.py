from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Articulo(Base):
    __tablename__ = "articulos"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(255), nullable=False)
    
    id_color = Column(Integer, ForeignKey("colores.id"))
    id_medida = Column(Integer, ForeignKey("medidas.id"))
    id_subfamilia = Column(Integer, ForeignKey("subfamilias.id"), nullable=True)
    id_articulo_precio = Column(Integer, ForeignKey("articulos_precio.id"), nullable=True)
    
    habilitado = Column(Boolean, default=True)

    color = relationship("Color")
    medida = relationship("Medida")
    subfamilia = relationship("SubFamilia", back_populates="articulos")
    articulo_precio = relationship("ArticuloPrecio")