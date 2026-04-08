from sqlalchemy import Column, Integer, String

from app.database import Base


class Color(Base):
    __tablename__ = "colores"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), nullable=True)
    descripcion = Column(String(100), nullable=True)
    color_hexa = Column(String(10), nullable=True)