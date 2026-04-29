from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from fastapi import UploadFile
from app.schemas import PagedResponse, ArticuloPrecioSchema, ArticuloSchema, ArticuloSugerencia


class IArticuloService(ABC):
    @abstractmethod
    def get_paginado(
        self,
        skip: Optional[int], 
        limit: Optional[int],
        filtro_codigo: Optional[str] = None,
        id_subfamilia: Optional[int] = None,
        id_articulo_precio: Optional[int] = None
    ) -> PagedResponse[ArticuloSchema] :
        """Trae los artículos envueltos en la lógica de paginación"""
        pass

    @abstractmethod
    def get_precio_paginado(
        self,
        skip: Optional[int], 
        limit: Optional[int],
        filtro_codigo: Optional[str] = None,
    ) -> PagedResponse[ArticuloPrecioSchema] :
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

    @abstractmethod
    async def subir_foto(self, articulo_precio_id: int, file: UploadFile) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_sugerencias(self, query_usuario: str) -> List[ArticuloSugerencia]:
        pass