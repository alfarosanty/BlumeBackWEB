from abc import ABC, abstractmethod
from typing import List
from app.models import Sector

class ISectorRepository(ABC):
    @abstractmethod
    def get_visible_sectores(self) -> List[Sector]:
        """Debe retornar solo los sectores con MostrarEnWeb = True"""
        pass

    @abstractmethod
    def get_all(self) -> List[Sector]:
        """Opcional: para el panel administrativo"""
        pass