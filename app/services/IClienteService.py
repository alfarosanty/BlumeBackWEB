from abc import ABC, abstractmethod
from typing import Optional

from app.models.Cliente import Cliente
from app.schemas.pagination import PagedResponse



class IClienteService(ABC):
    pass

    @abstractmethod
    def get_paginado(
        self,
        skip: int, 
        limit: int,
        id: Optional[int] = None,
    ) -> PagedResponse[Cliente] :
        """Trae los clientes envueltos en la lógica de paginación"""
        pass

    @abstractmethod
    def crear(self, razon_social: str, cuit: str, telefono: str) -> Cliente:
        """Crea un nuevo cliente en la base de datos."""
        pass

    @abstractmethod
    def actualizar(self, cliente: Cliente) -> Cliente:
        """Actualiza un cliente existente por su ID."""
        pass