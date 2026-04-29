import pandas as pd
from typing import Any, List, Optional, Dict
from fastapi import UploadFile, Depends
from app.database import get_db
from app.repositories.IArticuloRepository import IArticuloRepository
from app.repositories.imp.ArticuloRepository import ArticuloRepository
from app.schemas import PagedResponse, ArticuloPrecioSchema, ArticuloSchema, ArticuloSugerencia
from app.services.IArticuloService import IArticuloService
from pandas import DataFrame
from io import BytesIO
import cloudinary.uploader
from starlette.concurrency import run_in_threadpool
from nltk.stem import SnowballStemmer
import re

FOLDER_ARTICULOS = "alfa_soluciones/articulos"

class ArticuloService(IArticuloService):

    articuloRepository: IArticuloRepository
    
    def __init__(self, articuloRepository: IArticuloRepository) -> None:
        self.articuloRepository = articuloRepository
        self.stemmer = SnowballStemmer('spanish')


    def get_paginado(
        self, 
        skip: Optional[int], 
        limit: Optional[int], 
        filtro_codigo: Optional[str] = None,
        id_subfamilia: Optional[int] = None,
        id_articulo_precio: Optional[int] = None
    ) -> PagedResponse[ArticuloSchema]:
        return self.articuloRepository.get_paginado(
            skip=skip,
            limit=limit,
            filtro_codigo=filtro_codigo,
            id_subfamilia=id_subfamilia,
            id_articulo_precio=id_articulo_precio
        )
    
    def get_precio_paginado(
        self, 
        skip: Optional[int], 
        limit: Optional[int], 
        filtro_codigo: Optional[str] = None,
    ) -> PagedResponse[ArticuloPrecioSchema]:
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
                'ID': 'id',
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

            # 1. LIMPIEZA TOTAL: Eliminamos espacios al inicio/final y pasamos a mayúsculas
            df.columns = df.columns.str.strip().str.upper()

            mapeo = {
                'ID': 'id',
                'CODIGO': 'codigo',
                'DESCRIPCION': 'descripcion',
                'ID_COLOR': 'id_color',
                'ID_MEDIDA': 'id_medida',
                'ID_SUB_FAMILIA': 'id_subfamilia',
                'ID_ARTICULO_PRECIO': 'id_articulo_precio',
                'HABILITADO': 'habilitado'
            }

            # 2. Seleccionamos solo las columnas que están en nuestro mapeo
            columnas_a_usar = [c for c in mapeo.keys() if c in df.columns]
            df_final = df[columnas_a_usar].rename(columns=mapeo)

            # 3. Tratamiento de valores nulos
            df_final = df_final.fillna({
                'codigo': '',
                'descripcion': '',
                'id_articulo_precio': 0.0,
                'id_color': 0.0,
                'id_medida': 0.0,
                'id_subfamilia': 0.0,
                'habilitado': False
            })

            # 4. CONVERSIÓN DE BOOLEANO: El paso que nos faltaba
            # Si la columna existe, convertimos el "SI" (o cualquier cosa) a True/False
            if 'habilitado' in df_final.columns:
                df_final['habilitado'] = df_final['habilitado'].apply(
                    lambda x: True if str(x).strip().upper() == 'SI' else False
                )

            articulos_dict: List[Dict[str, Any]] = [
                    {str(k): v for k, v in record.items()} 
                    for record in df_final.to_dict(orient='records')
                ]
            
            print(f"Total de filas listas para subir: {len(articulos_dict)}")

            return self.articuloRepository.sync_articulos(articulos_dict)

        except Exception as e:
            print(f"--- ERROR EN LA IMPORTACIÓN --- {str(e)}")
            raise RuntimeError(f"Error procesando el Excel de articulos: {str(e)}")
    

    async def subir_foto(self, articulo_precio_id: int, file: UploadFile):
        try:
            upload_result = await run_in_threadpool(
                cloudinary.uploader.upload,
                file.file,
                folder=FOLDER_ARTICULOS,
                public_id=f"prod_{articulo_precio_id}",
                overwrite=True
            )
            
            url_foto = upload_result["secure_url"]
            self.articuloRepository.actualizar_url_foto(articulo_precio_id, url_foto)
            
            return {"url": url_foto}
        
        except Exception as e:
            print(f"Error subiendo a Cloudinary: {e}")
            raise Exception("No se pudo procesar la imagen")
        


    def get_sugerencias(self, query_usuario: str) -> List[ArticuloSugerencia]:
        query_limpia = re.sub(r'[^\w\s]', '', query_usuario.lower())
        palabras = query_limpia.split()
        
        if not palabras: return []
        
        terminos = []
        for p in palabras:
            raiz = self.stemmer.stem(p)
            # Mandamos la palabra con asterisco (como gallo*) 
            # Y la raíz sola para que MySQL decida qué tanto se parecen.
            terminos.append(f"{p}* {raiz}*")
        
        query_booleana = " ".join(terminos)
        return self.articuloRepository.get_sugerencias(query_booleana)


def get_articulo_service(db: Any = Depends(get_db)) -> ArticuloService:
    repository = ArticuloRepository(db)
    return ArticuloService(repository)