from abc import ABC, abstractmethod

class IArticuloMaestroXArticuloPrecioRepository(ABC):
    @abstractmethod
    def bulk_vincular(self, lista_vinculos: list[dict]):
        pass