import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from app.models.ArticuloMaestro import ArticuloMaestro
from app.repositories.imp.ArticuloMaestroRepository import ArticuloMaestroRepository
from app.services.IArticuloMaestroService import IArticuloMaestroService

class ArticuloMaestroService(IArticuloMaestroService):
    def __init__(self, db: Session):
        self.db = db
        self.repo = ArticuloMaestroRepository(db)

    def subir_maestros_desde_excel(self, file) -> int:
        if hasattr(file, 'filename') and file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        df = df.replace({np.nan: None})
        
        data_maestra = [
            {
                "codigo": row['CODIGO'], 
                "descripcion": row['DESCRIPCION'],
                "activo": bool(int(row['ACTIVO'])) if row['ACTIVO'] is not None else True
            }
            for _, row in df.iterrows()
        ]
        
        self.repo.bulk_insert_maestros(data_maestra)
        self.db.commit()
        
        return len(data_maestra)
    

    def obtener_todos(self, solo_activos: bool) -> list[ArticuloMaestro]:
        return self.repo.get_all_maestros(solo_activos)