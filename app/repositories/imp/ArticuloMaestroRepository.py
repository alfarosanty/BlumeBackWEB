from sqlalchemy import insert, select
from sqlalchemy.orm import Session, joinedload
from app.models.ArticuloMaestro import ArticuloMaestro
from app.repositories.IArticuloMaestroRepository import IArticuloMaestroRepository

# 2. La clase DEBE heredar de la interfaz en los paréntesis
class ArticuloMaestroRepository(IArticuloMaestroRepository):
    def __init__(self, session: Session):
        self.session = session

    # 3. El nombre y la indentación tienen que ser exactos a la interfaz
    def bulk_insert_maestros(self, lista_maestros: list[dict]):
        if not lista_maestros:
            return

        maestros_unicos_excel = {m['codigo']: m for m in lista_maestros}.values()
        codigos_nuevos = {m['codigo'] for m in maestros_unicos_excel}
        
        query_existentes = select(ArticuloMaestro.codigo).where(ArticuloMaestro.codigo.in_(codigos_nuevos))
        existentes = set(self.session.execute(query_existentes).scalars().all())

        maestros_a_insertar = [
            m for m in maestros_unicos_excel if m['codigo'] not in existentes
        ]

        if maestros_a_insertar:
            self.session.execute(
                insert(ArticuloMaestro),
                maestros_a_insertar
            )


    def get_all_maestros(self, solo_activos: bool) -> list[ArticuloMaestro]:
        # 1. Armamos la consulta base con la relación
        stmt = select(ArticuloMaestro).options(joinedload(ArticuloMaestro.variantes))
        
        # 2. Si el parámetro es True, aplicamos el filtro condicional
        if solo_activos:
            stmt = stmt.where(ArticuloMaestro.activo == True) # También podés usar ArticuloMaestro.activo.is_(True)
            
        result = self.session.execute(stmt)
        
        # Mantenemos el casteo a list() para que Pylance no se queje
        return list(result.scalars().unique().all())