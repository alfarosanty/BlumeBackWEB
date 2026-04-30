from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Mapping, Optional
from app.schemas import ArticuloPrecioSchema, ArticuloSchema, PagedResponse, ArticuloSugerencia

class IArticuloRepository(ABC):
    
    @abstractmethod
    def get_paginado(
        self, 
        skip: Optional[int], 
        limit: Optional[int], 
        filtro_codigo: Optional[str] = None,
        id_subfamilia: Optional[int] = None,
        id_articulo_precio: Optional[int] = None
    ) -> PagedResponse[ArticuloSchema]:
        """Trae los artículos envueltos en la lógica de paginación"""
        pass

    @abstractmethod
    def get_precio_paginado(self, skip: int, 
                            limit: int, 
                            filtro_codigo: Optional[str] = None, 
                            sector_id: Optional[int] = None, 
                            familia_id: Optional[int] = None, 
                            subfamilia_id: Optional[int] = None) -> PagedResponse[ArticuloPrecioSchema]:
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

    @abstractmethod
    def actualizar_url_foto(self, articulo_precio_id: int, url: str) -> None:
        """
        Actualiza el campo url_foto para un artículo dado.
        """
        pass

    @abstractmethod
    def get_sugerencias(self, query_booleana: str) -> List[ArticuloSugerencia]:
        pass