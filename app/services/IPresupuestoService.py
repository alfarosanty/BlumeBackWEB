from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from app.models import Presupuesto
from app.models.Usuario import Usuario
from app.schemas.PresupuestoSchema import PresupuestoCreate, PresupuestoFiltros, PresupuestoUpdate
from app.schemas.pagination import PagedResponse


class IPresupuestoService(ABC):

    @abstractmethod
    def obtener_presupuestos_filtrados(self, filtros: PresupuestoFiltros, auth: Usuario) -> PagedResponse[Presupuesto]:
        """Obtiene los presupuestos filtrados"""
        pass

    @abstractmethod
    def crear(self, presupuesto: PresupuestoCreate) -> Presupuesto:
        """Crea un nuevo presupuesto en la base de datos."""
        pass

    @abstractmethod
    def get_by_id(self, presupuesto_id: int) -> Optional[Presupuesto]:
        """Obtiene un presupuesto por su ID."""
        pass
    
    @abstractmethod
    def actualizar(self, presupuesto_id: int, presupuesto_in: PresupuestoUpdate) -> Presupuesto:
        """Recibe el ID y el Schema con los cambios."""
        pass
