from abc import ABC, abstractmethod
from typing import Optional
from app.models import Articulo, ArticuloPrecio
from app.schemas.pagination import PagedResponse


class IArticuloService(ABC):
    @abstractmethod
    def get_paginado(
        self,
        skip: int, 
        limit: int,
        filtro_codigo: Optional[str] = None,
        id_subfamilia: Optional[int] = None,
        id_articulo_precio: Optional[int] = None
    ) -> PagedResponse[Articulo] :
        """Trae los artículos envueltos en la lógica de paginación"""
        pass

    @abstractmethod
    def get_precio_paginado(
        self,
        skip: int, 
        limit: int,
        filtro_codigo: Optional[str] = None,
    ) -> PagedResponse[ArticuloPrecio] :
        """Trae los artículos precios envueltos en la lógica de paginación"""
        pass

    @abstractmethod
    def procesar_upsert_precios(self, file) -> int:
        """
        Procesa un archivo Excel para actualizar los precios de los artículos.
        Retorna un diccionario con el resultado del proceso.
        """
        pass

    @abstractmethod
    def procesar_excel_articulos(self, file) -> int:
        """
        Procesa un archivo Excel para actualizar los datos de los artículos.
        Retorna un diccionario con el resultado del proceso.
        """
        pass