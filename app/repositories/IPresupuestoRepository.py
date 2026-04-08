
from abc import ABC, abstractmethod
from typing import Any

from app.models import Presupuesto
from app.schemas.pagination import PagedResponse



class IPresupuestoRepository(ABC):
    
    @abstractmethod
    def get_paginado(
        self, 
        skip: int, 
        limit: int, 
        cliente_id: Any = None,
        estado: Any = None,
        desde: Any = None,
        hasta: Any = None
    ) -> PagedResponse[Presupuesto] : 
        """Trae los presupuestos envueltos en la lógica de paginación"""
    pass

    @abstractmethod
    def crear(self, presupuesto: Presupuesto) -> Presupuesto:
        """Crea un nuevo presupuesto en la base de datos."""
    pass

    @abstractmethod
    def get_by_id(self, presupuesto_id: int) -> Presupuesto:
        """Obtiene un presupuesto por su ID."""
    pass

    @abstractmethod
    def actualizar(self, presupuesto: Presupuesto) -> Presupuesto:
        """Actualiza un presupuesto existente por su ID."""
    pass

