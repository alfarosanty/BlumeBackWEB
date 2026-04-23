from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    # El email es lo que usaremos para el login
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Metadata útil
    is_active = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # LA LLAVE CLAVE: 
    # Mantenemos tu lógica de Multi-tenant
    confirmado = Column(Boolean, nullable=False, default=False)
    rol = Column(String(20), default="client")
    id_cliente = Column(Integer, ForeignKey("clientes.id"))
    
    # Relación
    cliente = relationship("Cliente", back_populates="usuario")