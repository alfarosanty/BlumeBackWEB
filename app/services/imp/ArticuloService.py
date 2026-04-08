import pandas as pd
from typing import Any, Optional, Dict
from fastapi import UploadFile, Depends
from app.database import get_db
from app.models import Articulo, ArticuloPrecio
from app.repositories.IArticuloRepository import IArticuloRepository
from app.repositories.imp.ArticuloRepository import ArticuloRepository
from app.schemas.pagination import PagedResponse
from app.services.IArticuloService import IArticuloService
from pandas import DataFrame
from io import BytesIO

class ArticuloService(IArticuloService):

    articuloRepository: IArticuloRepository
    
    def __init__(self, articuloRepository: IArticuloRepository) -> None:
        self.articuloRepository = articuloRepository


    def get_paginado(
        self, 
        skip: int, 
        limit: int, 
        filtro_codigo: Optional[str] = None,
        id_subfamilia: Optional[int] = None,
        id_articulo_precio: Optional[int] = None
    ) -> PagedResponse[Articulo]:
        return self.articuloRepository.get_paginado(
            skip=skip,
            limit=limit,
            filtro_codigo=filtro_codigo,
            id_subfamilia=id_subfamilia,
            id_articulo_precio=id_articulo_precio
        )
    
    def get_precio_paginado(
        self, 
        skip: int, 
        limit: int, 
        filtro_codigo: Optional[str] = None,
    ) -> PagedResponse[ArticuloPrecio]:
        return self.articuloRepository.get_precio_paginado(
            skip=skip,
            limit=limit,
            filtro_codigo=filtro_codigo,
        )
      
    def procesar_upsert_precios(self, file: UploadFile) -> int:
        try:
            contenido = file.file.read()
            df: DataFrame = pd.read_excel(BytesIO(contenido))

            mapeo = {
                'ID_ARTICULO_PRECIO': 'id',
                'CODIGO': 'codigo',
                'DESCRIPCION': 'descripcion',
                'PRECIO1': 'precio1',
                'PRECIO2': 'precio2',
                'PRECIO3': 'precio3'
            }

            df_final = df[list(mapeo.keys())].rename(columns=mapeo)

            df_final = df_final.fillna({
                'precio1': 0.0,
                'precio2': 0.0,
                'precio3': 0.0,
                'descripcion': ''
            })

            # Cada dict es: {"id": 123, "precio1": 500.0, ...}
            precios_dict: List[Dict[str, Any]] = df_final.to_dict(orient='records') # type: ignore

            return self.articuloRepository.sync_precios(precios_dict)
        except Exception as e:
            raise RuntimeError(f"Error procesando el Excel de precios: {str(e)}")
    
    def procesar_excel_articulos(self, file: UploadFile) -> int:
        try:
            contenido = file.file.read()
            df: DataFrame = pd.read_excel(BytesIO(contenido))

            mapeo = {
                'ID_ARTICULO': 'id',
                'CODIGO': 'codigo',
                'DESCRIPCION': 'descripcion',
                'ID_ARTICULO_PRECIO': 'id_articulo_precio',
                'ID_COLOR': 'id_color',
                'ID_MEDIDA': 'id_medida',
                'ID_SUBFAMILIA' : 'id_subfamilia',
                'HABILITADO' : 'habilitado'
            }


            df_final = df[list(mapeo.keys())].rename(columns=mapeo)

            df_final = df_final.fillna({
                'codigo': '',
                'descripcion': '',
                'id_articulo_precio': 0.0,
                'id_color': 0.0,
                'id_medida': 0.0,
                'id_subfamilia': 0.0,
                'habilitado': False
            })

            articulos_dict: List[Dict[str, Any]] = df_final.to_dict(orient='records') # type: ignore
            return self.articuloRepository.sync_articulos(articulos_dict)


        except Exception as e:
            raise RuntimeError(f"Error procesando el Excel de articulos: {str(e)}")


def get_articulo_service(db: Any = Depends(get_db)) -> ArticuloService:
    repository = ArticuloRepository(db)
    return ArticuloService(repository)