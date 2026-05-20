from abc import ABC, abstractmethod
from typing import Any, Optional

from app.models import ArticuloMaestro
from app.schemas.ArticuloMaestroSchema import ArticuloMaestroDto


class IArticuloMaestroService(ABC):

    @abstractmethod
    def subir_maestros_desde_excel(self, file: Any) -> int:
        pass

    @abstractmethod
    def obtener_todos(self, solo_activos: bool, skip: Optional[int] = 0, limit: Optional[int] = 20) -> list[ArticuloMaestro]:
        pass

    @abstractmethod
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
        """Retorna (total, lista de DTOs completos) con subfamilia→familia→sector y variantes con medida."""