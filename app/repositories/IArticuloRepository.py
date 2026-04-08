from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Mapping, Optional
from app.models import Articulo, ArticuloPrecio
from app.schemas.pagination import PagedResponse

class IArticuloRepository(ABC):
    
    @abstractmethod
    def get_paginado(
        self, 
        skip: int, 
        limit: int, 
        filtro_codigo: Optional[str] = None,
        id_subfamilia: Optional[int] = None,
        id_articulo_precio: Optional[int] = None
    ) -> PagedResponse[Articulo]:  # <-- El contrato ya exige el objeto página
        """Trae los artículos envueltos en la lógica de paginación"""
        pass

    @abstractmethod
    def get_precio_paginado(
        self, 
        skip: int, 
        limit: int, 
        filtro_codigo: Optional[str] = None,
    ) -> PagedResponse[ArticuloPrecio]:  # <-- El contrato ya exige el objeto página
        """Trae los artículos precios envueltos en la lógica de paginación"""
        pass

    @abstractmethod
    def sync_precios(self, mappings: Iterable[Dict[str, Any]]) -> int:
        """
        Sincroniza precios: Si el ID existe, actualiza. Si no, inserta.
        Recibe una lista de diccionarios con la data limpia.
        """
        pass

    @abstractmethod
    def sync_articulos(self, mappings: Iterable[Mapping[str, Any]]) -> int:
        """
        Sincroniza artículos: Si el ID existe, actualiza. Si no, inserta.
        Recibe una lista de diccionarios con la data limpia.
        """
        pass