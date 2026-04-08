from typing import Any
from fastapi import Depends
from app.database import get_db
from app.models.Cliente import Cliente
from app.repositories.IClienteRepository import IClienteRepository
from app.repositories.imp.ClienteRepository import ClienteRepository
from app.services.IClienteService import IClienteService


class ClienteService(IClienteService):
    clienteRepository: IClienteRepository

    def __init__(self, clienteRepository: IClienteRepository):
        self.clienteRepository = clienteRepository

    def get_paginado(
        self, 
        skip: int, 
        limit: int, 
        id: Any = None
    ):
        return self.clienteRepository.get_paginado(
            skip=skip,
            limit=limit,
            id=id
        )
    
    def crear(self, cliente: Cliente) -> Cliente:
        return self.clienteRepository.crear(cliente)
    
    def actualizar(self, cliente: Cliente) -> Cliente:
        return self.clienteRepository.actualizar(cliente)



def get_cliente_service(db: Any = Depends(get_db)) -> ClienteService:
    repository = ClienteRepository(db)
    return ClienteService(repository)