from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class ArticuloPresupuesto(Base):
    __tablename__ = "articulos_presupuesto"

    id = Column(Integer, primary_key=True, index=True)
    fecha_creacion = Column(DateTime, default=datetime.now)

    id_presupuesto = Column(Integer, ForeignKey("presupuestos.id"))
    id_articulo = Column(Integer, ForeignKey("articulos.id"))

    cantidad = Column(Integer, nullable=False)
    cantidad_pendiente = Column(Integer, nullable=True)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    descuento = Column(Numeric(10, 2), default=0.0)
    descripcion = Column(String(255), nullable=True)
    codigo = Column(String(50), nullable=True)
    
    hay_stock = Column(Boolean, default=True)
    producir = Column(Boolean, default=False)

    # Relaciones
    presupuesto = relationship("Presupuesto", back_populates="articulos")
    articulo = relationship("Articulo")