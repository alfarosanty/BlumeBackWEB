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

        if cliente_id is not None:
            query = query.filter(Presupuesto.cliente_id == cliente_id)
        
        if estado is not None:
            query = query.filter(Presupuesto.estado == estado)
        
        if desde is not None:
            query = query.filter(Presupuesto.fecha >= desde)
        
        if hasta is not None:
            query = query.filter(Presupuesto.fecha <= hasta)

        total = query.count()
        items = query.options(
            joinedload(Presupuesto.cliente),
            joinedload(Presupuesto.articulos).options(
                joinedload(ArticuloPresupuesto.articulo).options(
                    joinedload(Articulo.color),
                    joinedload(Articulo.medida),
                    joinedload(Articulo.subfamilia)
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
        presupuesto_en_db = self.db.query(Presupuesto).filter(Presupuesto.id == presupuesto.id).first()
        if not presupuesto_en_db:
            raise Exception("Presupuesto no encontrado")

        presupuesto_en_db.id_cliente = presupuesto.id_cliente
        presupuesto_en_db.fecha = presupuesto.fecha
        presupuesto_en_db.estado = presupuesto.estado

        self.db.commit()
        self.db.refresh(presupuesto_en_db)
        return presupuesto_en_db