from collections import defaultdict
from typing import Any, Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ArticuloMaestro
from app.repositories.IArticuloMaestroRepository import IArticuloMaestroRepository
from app.repositories.imp.ArticuloMaestroRepository import ArticuloMaestroRepository
from app.schemas.ArticuloMaestroSchema import (
    ArticuloPrecioConMedidaDto,
    ArticuloMaestroDto,
    FamiliaConSectorDto,
    MedidaDto,
    SectorDto,
    SubFamiliaConJerarquiaDto,
)
from app.services.IArticuloMaestroService import IArticuloMaestroService


class ArticuloMaestroService(IArticuloMaestroService):

    def __init__(self, repo: IArticuloMaestroRepository):
        self.repo = repo

    def subir_maestros_desde_excel(self, file: Any) -> int:
        raise NotImplementedError("Usar ArticuloService para la carga masiva desde Excel")

    def obtener_todos(self, solo_activos: bool, skip: Optional[int] = 0, limit: Optional[int] = 20) -> list[ArticuloMaestro]:
        total, items = self.repo.obtener_paginado(
            solo_activos=solo_activos, codigo=None, sector_id=None,
            familia_id=None, subfamilia_id=None, skip=skip or 0, limit=limit or 20
        )
        return items

    def obtener_paginado(
        self,
        solo_activos: Optional[bool],
        codigo: Optional[str],
        sector_id: Optional[int],
        familia_id: Optional[int],
        subfamilia_id: Optional[int],
        page_number: int,
        page_size: int,
    ) -> tuple[int, list[ArticuloMaestroDto]]:
        skip = (page_number - 1) * page_size
        total, maestros = self.repo.obtener_paginado(
            solo_activos=solo_activos,
            codigo=codigo,
            sector_id=sector_id,
            familia_id=familia_id,
            subfamilia_id=subfamilia_id,
            skip=skip,
            limit=page_size,
        )

        if not maestros:
            return total, []

        maestro_ids = [m.id for m in maestros]

        junctions = self.repo.obtener_junctions_con_detalle(maestro_ids)

        junctions_por_maestro: dict[int, list] = defaultdict(list)
        ap_ids: set[int] = set()
        for j in junctions:
            junctions_por_maestro[j.articulo_maestro_id].append(j)
            ap_ids.add(j.articulo_precio_id)

        primer_art_por_ap = self.repo.obtener_primer_articulo_por_ap(list(ap_ids)) if ap_ids else {}

        dtos = [
            self._ensamblar_dto(m, junctions_por_maestro, primer_art_por_ap)
            for m in maestros
        ]
        return total, dtos

    def _ensamblar_dto(self, maestro, junctions_por_maestro, primer_art_por_ap) -> ArticuloMaestroDto:
        mis_junctions = junctions_por_maestro.get(maestro.id, [])
        primer_junction = mis_junctions[0] if mis_junctions else None

        variantes = []
        for j in mis_junctions:
            ap = j.articulo_precio
            art = primer_art_por_ap.get(j.articulo_precio_id)

            medida_dto = None
            if art and art.medida:
                m = art.medida
                medida_dto = MedidaDto(id=m.id, codigo=m.codigo, descripcion=m.descripcion)

            variantes.append(ArticuloPrecioConMedidaDto(
                id=ap.id,
                codigo=ap.codigo,
                descripcion=ap.descripcion,
                precio1=float(ap.precio1 or 0),
                precio2=float(ap.precio2 or 0),
                precio3=float(ap.precio3 or 0),
                habilitado=ap.habilitado,
                medida=medida_dto,
            ))

        subfamilia_dto = None
        if primer_junction and primer_junction.subfamilia:
            sf = primer_junction.subfamilia
            familia_dto = None
            if sf.familia:
                fam = sf.familia
                sector_dto = None
                if fam.sector:
                    s = fam.sector
                    sector_dto = SectorDto(id=s.id, codigo=s.codigo, descripcion=s.descripcion)
                familia_dto = FamiliaConSectorDto(id=fam.id, descripcion=fam.descripcion, sector=sector_dto)
            subfamilia_dto = SubFamiliaConJerarquiaDto(id=sf.id, descripcion=sf.descripcion, familia=familia_dto)

        return ArticuloMaestroDto(
            id=maestro.id,
            codigo=maestro.codigo,
            descripcion=maestro.descripcion,
            url_foto=maestro.url_foto,
            activo=maestro.activo,
            subfamilia=subfamilia_dto,
            variantes=variantes,
        )


def get_articulo_maestro_service(db: Session = Depends(get_db)) -> IArticuloMaestroService:
    return ArticuloMaestroService(ArticuloMaestroRepository(db))
