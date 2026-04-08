from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255))
    
    # LA LLAVE CLAVE:
    # Si es NULL, es un Admin o SuperUser.
    # Si tiene número, es un cliente específico.
    id_cliente = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    
    cliente = relationship("Cliente", back_populates="usuario")