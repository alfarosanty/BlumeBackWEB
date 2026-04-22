from sqlalchemy import Column, Integer, String,  Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models import CondicionFiscal

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    razon_social = Column(String(150), nullable=False)
    contacto = Column(String(100), nullable=True)
    telefono = Column(String(50), nullable=True)
    domicilio = Column(String(255), nullable=True)
    localidad = Column(String(100), nullable=True)
    provincia = Column(String(100), nullable=True)
    cuit = Column(String(20), nullable=True)
    transporte = Column(String(100), nullable=True)
    condicion_fiscal = Column(SQLEnum(CondicionFiscal), default=CondicionFiscal.CONSUMIDOR_FINAL)
    # El link a tu ERP de escritorio
    id_cliente_local = Column(Integer, nullable=True)
    # El cliente sabe quién es su usuario (opcional, para conveniencia)
    usuario = relationship("Usuario", back_populates="cliente", uselist=False)
    presupuestos = relationship("Presupuesto", back_populates="cliente")