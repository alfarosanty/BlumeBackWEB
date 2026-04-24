from typing import Any 
from app.models import Articulo, Presupuesto
from app.models.ArticuloPresupuesto import ArticuloPresupuesto
from app.repositories.IPresupuestoRepository import IPresupuestoRepository
from sqlalchemy.orm import Session, joinedload
from app.schemas.pagination import PagedResponse



class PresupuestoRepository(IPresupuestoRepository):

    db: Session

    def __init__(self, db: Session):
        """Recibe la sesión de base de datos (Inyección de dependencia manual)"""
        self.db = db

    def get_paginado(
        self, 
        skip: int, 
        limit: int, 
        cliente_id: Any = None,
        estado: Any = None,
        desde: Any = None,
        hasta: Any = None
    ):
        query = self.db.query(Presupuesto)

        # Filtros
        if cliente_id is not None:
            query = query.filter(Presupuesto.id_cliente == cliente_id)
        if estado is not None:
            query = query.filter(Presupuesto.estado == estado)
        if desde is not None:
            query = query.filter(Presupuesto.fecha >= desde)
        if hasta is not None:
            query = query.filter(Presupuesto.fecha <= hasta)

        total = query.count()

        # Medir la CARGA DE DATOS (Segundo culpable potencial)
        items = query.options(
            joinedload(Presupuesto.cliente),
            joinedload(Presupuesto.articulos).options(
                joinedload(ArticuloPresupuesto.articulo).options(
                    joinedload(Articulo.color),
                    joinedload(Articulo.medida),
                    joinedload(Articulo.subfamilia),
                    joinedload(Articulo.articulo_precio)
                )
            )
        ).offset(skip).limit(limit).all()

        return PagedResponse.crear(
            items=items, 
            total=total, 
            skip=skip, 
            limit=limit
        )
    

    def crear(self, presupuesto: Presupuesto):
        self.db.add(presupuesto)
        self.db.commit()
        self.db.refresh(presupuesto)
        return presupuesto
    
    def get_by_id(self, presupuesto_id: int):
        return self.db.query(Presupuesto).options(joinedload(Presupuesto.cliente)).filter(Presupuesto.id == presupuesto_id).first()
    
    def actualizar(self, presupuesto: Presupuesto) -> Presupuesto:     
        try:
            self.db.add(presupuesto)
            self.db.commit()
            self.db.refresh(presupuesto)
            return presupuesto
        except Exception as e:
            self.db.rollback()
            raise e