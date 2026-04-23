from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from app.models import Presupuesto
from app.schemas.PresupuestoSchema import PresupuestoFiltros
from app.schemas.pagination import PagedResponse


class IPresupuestoService(ABC):

    @abstractmethod
    def get_paginado(
        self,
        skip: int, 
        limit: int,
        cliente_id: Optional[int] = None,
        estado: Optional[str] = None,
        desde: Optional[date] = None,
        hasta: Optional[date] = None
    ) -> PagedResponse[Presupuesto] :
        """Trae los presupuestos envueltos en la lógica de paginación"""
        pass

    @abstractmethod
    def crear(self, presupuesto: Presupuesto) -> Presupuesto:
        """Crea un nuevo presupuesto en la base de datos."""
        pass

    @abstractmethod
    def get_by_id(self, presupuesto_id: int) -> Optional[Presupuesto]:
        """Obtiene un presupuesto por su ID."""
        pass
    
    @abstractmethod
    def actualizar(self, presupuesto: Presupuesto) -> Presupuesto:
        """Actualiza un presupuesto existente por su ID."""
        pass

    @abstractmethod
    def obtener_presupuestos_filtrados(self, filtros: PresupuestoFiltros, auth: dict) -> PagedResponse[Presupuesto]:
        """Obtiene los presupuestos filtrados"""
        pass