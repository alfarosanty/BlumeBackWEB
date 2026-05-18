from sqlalchemy import insert
from sqlalchemy.orm import Session
from app.models import ArticuloMaestroXArticuloPrecio
from app.repositories.IArticuloMaestroXArticuloPrecio import IArticuloMaestroXArticuloPrecioRepository

class ArticuloMaestroXArticuloPrecioRepository(IArticuloMaestroXArticuloPrecioRepository):
    def __init__(self, session: Session):
        self.session = session

    def bulk_vincular(self, lista_vinculos: list[dict]):
        if not lista_vinculos:
            return

        # Al usar SQLAlchemy Core (insert masivo), es sumamente veloz
        self.session.execute(
            insert(ArticuloMaestroXArticuloPrecio),
            lista_vinculos
        )