from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.SubFamilia import SubFamilia
    from app.models.ArticuloPrecio import ArticuloPrecio


class ArticuloMaestroXArticuloPrecio(Base):
    __tablename__ = "ArticuloMaestroXArticuloPrecio"

    # Mantenemos snake_case en Python, pero apuntamos al nombre real de la columna en la BD
    id: Mapped[int] = mapped_column("Id", Integer, primary_key=True)
    articulo_maestro_id: Mapped[int] = mapped_column("ArticuloMaestroId", Integer, ForeignKey("ArticuloMaestro.id"))
    articulo_precio_id: Mapped[int] = mapped_column("ArticuloPrecioId", Integer, ForeignKey("articulos_precio.id"))
    subfamilia_id: Mapped[int] = mapped_column("SubFamiliaId", Integer, ForeignKey("subfamilias.id"))

    # Relaciones lazy (no afectan queries existentes; se usan con joinedload explícito)
    subfamilia: Mapped[Optional["SubFamilia"]] = relationship(
        "SubFamilia", foreign_keys=[subfamilia_id], lazy="select"
    )
    articulo_precio: Mapped[Optional["ArticuloPrecio"]] = relationship(
        "ArticuloPrecio", foreign_keys=[articulo_precio_id], lazy="select",
        overlaps="maestros,variantes"
    )