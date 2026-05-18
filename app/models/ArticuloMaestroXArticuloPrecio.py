from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class ArticuloMaestroXArticuloPrecio(Base):
    __tablename__ = "ArticuloMaestroXArticuloPrecio"

    # Mantenemos snake_case en Python, pero apuntamos al nombre real de la columna en la BD
    id: Mapped[int] = mapped_column("Id", Integer, primary_key=True)
    articulo_maestro_id: Mapped[int] = mapped_column("ArticuloMaestroId", Integer, ForeignKey("ArticuloMaestro.id"))
    articulo_precio_id: Mapped[int] = mapped_column("ArticuloPrecioId", Integer, ForeignKey("articulos_precio.id"))
    subfamilia_id: Mapped[int] = mapped_column("SubFamiliaId", Integer, ForeignKey("subfamilias.id"))