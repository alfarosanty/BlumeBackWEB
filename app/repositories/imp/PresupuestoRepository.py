from typing import Any

from sqlalchemy import func 
from app.models import Articulo, Familia, Presupuesto, SubFamilia
from app.models.ArticuloPresupuesto import ArticuloPresupuesto
from app.repositories.IPresupuestoRepository import IPresupuestoRepository
from sqlalchemy.orm import Session, joinedload
from app.schemas.pagination import PagedResponse
import time



class PresupuestoRepository(IPresupuestoRepository):

    db: Session
    def __init__(self, db: Session):
        """Recibe la sesión de base de datos (Inyección de dependencia manual)"""
        self.db = db

    presupuesto_options = [
        joinedload(Presupuesto.cliente),
        joinedload(Presupuesto.articulos).options(
            joinedload(ArticuloPresupuesto.articulo).options(
                joinedload(Articulo.color),
                joinedload(Articulo.medida),
                joinedload(Articulo.subfamilia).joinedload(SubFamilia.familia).joinedload(Familia.sector),
                joinedload(Articulo.articulo_precio)
            )
        )
    ]

    def get_paginado(self, skip: int, limit: int, cliente_id: Any = None, 
                    estado: Any = None, desde: Any = None, hasta: Any = None):
        query = self.db.query(Presupuesto)

        if cliente_id is not None:
            query = query.filter(Presupuesto.id_cliente == cliente_id)
        if estado is not None:
            query = query.filter(Presupuesto.estado == estado)
        if desde is not None:
            query = query.filter(Presupuesto.fecha_creacion >= desde)
        if hasta is not None:
            query = query.filter(Presupuesto.fecha_creacion <= hasta)

        total = query.count()

        items = query.options(*self.presupuesto_options)\
                    .order_by(Presupuesto.fecha_creacion.desc())\
                    .offset(skip).limit(limit).all()

        return PagedResponse.crear(items=items, total=total, skip=skip, limit=limit)

    def get_by_id(self, presupuesto_id: int):
        return self.db.query(Presupuesto)\
                    .options(*self.presupuesto_options)\
                    .filter(Presupuesto.id == presupuesto_id)\
                    .first()

    def crear(self, presupuesto: Presupuesto):
        max_nro = self.db.query(func.max(Presupuesto.numero_presupuesto_cliente))\
            .filter(Presupuesto.id_cliente == presupuesto.id_cliente)\
            .scalar()

        if max_nro is not None:
            presupuesto.numero_presupuesto_cliente = max_nro + 1
        else:
            presupuesto.numero_presupuesto_cliente = 1 # type: ignore
        
        self.db.add(presupuesto)
        
        try:
            self.db.commit()
            self.db.refresh(presupuesto)
            return presupuesto
        except Exception as e:
            self.db.rollback()
            raise e
    
    def actualizar(self, presupuesto: Presupuesto) -> Presupuesto:     
        try:
            self.db.add(presupuesto)
            self.db.commit()
            self.db.refresh(presupuesto)
            return presupuesto
        except Exception as e:
            self.db.rollback()
            raise e