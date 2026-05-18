from abc import ABC, abstractmethod

from app.models.ArticuloMaestro import ArticuloMaestro

class IArticuloMaestroRepository(ABC):
    @abstractmethod
    def bulk_insert_maestros(self, lista_maestros: list[dict]):
        pass

    @abstractmethod
    def get_all_maestros(self, solo_activos: bool) -> list[ArticuloMaestro]:
        pass