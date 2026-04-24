from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.models import EstadoPresupuesto

class Presupuesto(Base):
    __tablename__ = "presupuestos"

    id = Column(Integer, primary_key=True, index=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    id_cliente = Column(Integer, ForeignKey("clientes.id"))
    estado = Column(SQLEnum(EstadoPresupuesto), default=EstadoPresupuesto.CREADO)

    total = Column(Float, default=0.0)

    # Relaciones
    # cliente = relationship("Cliente", back_populates="presupuestos")
    articulos = relationship("ArticuloPresupuesto", back_populates="presupuesto")
    cliente = relationship("Cliente", back_populates="presupuestos")