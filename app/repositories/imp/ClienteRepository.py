from typing import Optional
from app.models import Cliente
from app.repositories.IClienteRepository import IClienteRepository
from sqlalchemy.orm import Session, joinedload

from app.schemas.pagination import PagedResponse

class ClienteRepository(IClienteRepository):

    db: Session

    def __init__(self, db: Session):
        """Recibe la sesión de base de datos (Inyección de dependencia manual)"""
        self.db = db


    def get_paginado(
        self, 
        skip: int, 
        limit: int, 
        id: Optional[int] = None
    ):
        query = self.db.query(Cliente)

        if id is not None:
            query = query.filter(Cliente.id == id)

        total = query.count()
        items = query.options(joinedload(Cliente.presupuestos)).offset(skip).limit(limit).all()

        return PagedResponse.crear(
                items=items, 
                total=total, 
                skip=skip, 
                limit=limit
            )
    
    def crear(self, cliente: Cliente) -> Cliente:
        self.db.add(cliente)
        self.db.commit()
        self.db.refresh(cliente)
        return cliente
    
    def actualizar(self, cliente: Cliente) -> Cliente:
        existing_cliente = self.db.query(Cliente).filter(Cliente.id == cliente.id).first()
        if not existing_cliente:
            raise Exception("Cliente no encontrado")

        existing_cliente.razon_social = cliente.razon_social
        existing_cliente.telefono = cliente.telefono

        self.db.commit()
        self.db.refresh(existing_cliente)
        return existing_cliente