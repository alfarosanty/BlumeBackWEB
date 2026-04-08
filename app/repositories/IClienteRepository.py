
from abc import ABC, abstractmethod
from typing import Any, Optional

from app.models.Cliente import Cliente
from app.schemas.pagination import PagedResponse


class IClienteRepository(ABC):
    
    @abstractmethod
    def get_paginado(
        self, 
        skip: int, 
        limit: int, 
        id: Optional[int] = None
    ) -> PagedResponse[Cliente]:
        """Trae los clientes envueltos en la lógica de paginación"""
    pass

    @abstractmethod
    def crear(self, cliente: Cliente) -> Cliente:
        """Crea un nuevo cliente en la base de datos"""
    pass

    @abstractmethod
    def actualizar(self, cliente: Cliente) -> Cliente:
        """Actualiza un cliente existente en la base de datos"""
    pass