from fastapi import HTTPException
import pandas as pd
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session
import logging


from app.models import Articulo, ArticuloMaestro
from app.repositories.imp.ArticuloMaestroXArticuloPrecioRepository import ArticuloMaestroXArticuloPrecioRepository
from app.services.IArticuloMaestroXArticuloPrecioService import IArticuloMaestroXArticuloPrecioService 

class ArticuloMaestroXArticuloPrecioService(IArticuloMaestroXArticuloPrecioService):
    def __init__(self, db: Session):
        self.db = db
        self.repo_intermedia = ArticuloMaestroXArticuloPrecioRepository(db)

    def vincular_articulos_por_ids(self, file: Any) -> int:
        # 1. Lectura del archivo (CSV o Excel)
        if hasattr(file, 'filename') and file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # 2. Mapa de Códigos -> ID de ArticuloMaestro
        stmt_maestros = select(ArticuloMaestro.id, ArticuloMaestro.codigo)
        maestros_db = self.db.execute(stmt_maestros).all()
        mapa_maestros = {m.codigo: m.id for m in maestros_db}

        stmt_articulos = select(Articulo.id_articulo_precio, Articulo.id_subfamilia).where(Articulo.id_articulo_precio.is_not(None))
        articulos_db = self.db.execute(stmt_articulos).all()
        
        mapa_subfamilias = {a.id_articulo_precio: a.id_subfamilia for a in articulos_db}

        vinculos_data = []

        # 4. Procesamos el DataFrame
        for _, row in df.iterrows():
            maestro_id = mapa_maestros.get(row['CODIGO'])
            
            if maestro_id and pd.notna(row['ARTICULO_PRECIO_RELACIONADO']):
                ids_precios = str(row['ARTICULO_PRECIO_RELACIONADO']).split(",")
                
                for p_id in ids_precios:
                    p_id_clean = p_id.strip()
                    if p_id_clean.isdigit():
                        precio_id = int(p_id_clean)
                        
                        # Buscamos en el mapa de la tabla Articulo
                        subfamilia_id = mapa_subfamilias.get(precio_id)
                        
                        if subfamilia_id:
                            # EL MAPEO CORRECTO:
                            # Usamos las propiedades exactas de la clase de Python
                            vinculos_data.append({
                                "articulo_maestro_id": maestro_id,
                                "articulo_precio_id": precio_id,
                                "subfamilia_id": subfamilia_id
                            })

        #print("👉 CONTENIDO DE VINCULOS_DATA:", vinculos_data[:2], flush=True)
        
        #if vinculos_data:
            # Esto va a cortar la ejecución y te va a mostrar el JSON real en tu navegador/Postman
        #    raise HTTPException(status_code=418, detail={
        #        "mensaje": "Inspeccionando datos antes del insert",
        #        "cantidad_registros": len(vinculos_data),
        #        "primer_registro_completo": vinculos_data[0]
        #    })

        # 5. Carga masiva en repositorio
        if vinculos_data:
            self.repo_intermedia.bulk_vincular(vinculos_data)
            self.db.commit()
        
        return len(vinculos_data)