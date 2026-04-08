from sqlalchemy import Column, Integer, String
from app.database import Base

class Medida(Base):
    __tablename__ = "medidas"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), nullable=True)
    descripcion = Column(String(100), nullable=True)