from abc import ABC, abstractmethod
from typing import Optional

from app.models.Articulo import Articulo
from app.models.ArticuloMaestro import ArticuloMaestro
from app.models.ArticuloMaestroXArticuloPrecio import ArticuloMaestroXArticuloPrecio


class IArticuloMaestroRepository(ABC):

    @abstractmethod
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
        """Retorna (total, lista paginada de ArticuloMaestro) con los filtros aplicados."""

    @abstractmethod
    def obtener_junctions_con_detalle(
        self, maestro_ids: list[int]
    ) -> list[ArticuloMaestroXArticuloPrecio]:
        """Retorna las filas de la tabla intermedia con subfamilia→familia→sector y articulo_precio precargados."""

    @abstractmethod
    def obtener_primer_articulo_por_ap(
        self, ap_ids: list[int]
    ) -> dict[int, Articulo]:
        """Retorna un dict {articulo_precio_id: primer_Articulo} para cargar la Medida."""
