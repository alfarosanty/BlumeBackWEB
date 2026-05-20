from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.Articulo import Articulo
from app.models.ArticuloMaestro import ArticuloMaestro
from app.models.ArticuloMaestroXArticuloPrecio import ArticuloMaestroXArticuloPrecio
from app.models.Familia import Familia
from app.models.SubFamilia import SubFamilia
from app.repositories.IArticuloMaestroRepository import IArticuloMaestroRepository


class ArticuloMaestroRepository(IArticuloMaestroRepository):

    def __init__(self, db: Session):
        self.db = db

    def obtener_paginado(
        self,
        solo_activos: Optional[bool],
        codigo: Optional[str],
        sector_id: Optional[int],
        familia_id: Optional[int],
        subfamilia_id: Optional[int],
        skip: int,
        limit: int,
    ) -> tuple[int, list[ArticuloMaestro]]:

        def _base_stmt(for_count: bool):
            if for_count:
                stmt = select(func.count(func.distinct(ArticuloMaestro.id)))
            else:
                stmt = select(ArticuloMaestro).distinct()

            # --- JOINs de clasificación (orden fijo, siempre juntos) ---
            necesita_clasificacion = any([sector_id, familia_id, subfamilia_id])

            if necesita_clasificacion:
                # 1. Tabla intermedia (base para los filtros de clasificación)
                stmt = stmt.join(
                    ArticuloMaestroXArticuloPrecio,
                    ArticuloMaestroXArticuloPrecio.articulo_maestro_id == ArticuloMaestro.id,
                )
                # 2. SubFamilia (necesaria para familia_id y sector_id)
                if familia_id or sector_id:
                    stmt = stmt.join(
                        SubFamilia,
                        SubFamilia.id == ArticuloMaestroXArticuloPrecio.subfamilia_id,
                    )
                    # 3. Familia (necesaria para sector_id)
                    if sector_id:
                        stmt = stmt.join(
                            Familia,
                            Familia.id == SubFamilia.id_familia,
                        )

            # --- WHERE clauses de clasificación ---
            if subfamilia_id:
                stmt = stmt.where(
                    ArticuloMaestroXArticuloPrecio.subfamilia_id == subfamilia_id
                )
            if familia_id:
                stmt = stmt.where(SubFamilia.id_familia == familia_id)
            if sector_id:
                stmt = stmt.where(Familia.id_sector == sector_id)

            # --- Filtro activo ---
            if solo_activos is True:
                stmt = stmt.where(ArticuloMaestro.activo == True)  # noqa: E712

            # --- Filtro codigo: match exacto case-insensitive sobre ArticuloMaestro.codigo ---
            if codigo:
                stmt = stmt.where(func.lower(ArticuloMaestro.codigo) == codigo.lower())

            return stmt

        total: int = self.db.execute(_base_stmt(for_count=True)).scalar() or 0

        rows = (
            self.db.execute(
                _base_stmt(for_count=False).offset(skip).limit(limit)
            )
            .scalars()
            .unique()
            .all()
        )

        return total, list(rows)

    def obtener_junctions_con_detalle(
        self, maestro_ids: list[int]
    ) -> list[ArticuloMaestroXArticuloPrecio]:
        if not maestro_ids:
            return []

        stmt = (
            select(ArticuloMaestroXArticuloPrecio)
            .where(ArticuloMaestroXArticuloPrecio.articulo_maestro_id.in_(maestro_ids))
            .options(
                joinedload(ArticuloMaestroXArticuloPrecio.subfamilia)
                .joinedload(SubFamilia.familia)
                .joinedload(Familia.sector),
                joinedload(ArticuloMaestroXArticuloPrecio.articulo_precio),
            )
        )

        return list(self.db.execute(stmt).scalars().unique().all())

    def obtener_primer_articulo_por_ap(
        self, ap_ids: list[int]
    ) -> dict[int, Articulo]:
        if not ap_ids:
            return {}

        subq = (
            select(func.min(Articulo.id).label("min_id"))
            .where(Articulo.id_articulo_precio.in_(ap_ids))
            .group_by(Articulo.id_articulo_precio)
            .subquery()
        )

        articulos = (
            self.db.execute(
                select(Articulo)
                .where(Articulo.id.in_(select(subq.c.min_id)))
                .options(joinedload(Articulo.medida))
            )
            .scalars()
            .all()
        )

        return {a.id_articulo_precio: a for a in articulos}
