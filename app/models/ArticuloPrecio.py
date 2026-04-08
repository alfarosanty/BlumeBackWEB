from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base

class ArticuloPrecio(Base):
    __tablename__ = "articulos_precio"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), nullable=True)
    descripcion = Column(String(255), nullable=True)
    precio1 = Column(Numeric(10, 2), default=0.0)
    precio2 = Column(Numeric(10, 2), default=0.0)
    precio3 = Column(Numeric(10, 2), default=0.0)
