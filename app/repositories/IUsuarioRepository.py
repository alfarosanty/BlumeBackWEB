from abc import ABC, abstractmethod

from app.models.Usuario import Usuario


class IUsuarioRepository(ABC):
    
    @abstractmethod
    def create(self, usuario: Usuario) -> Usuario :
        """ Crea al usuario nuevo en la base de datos. """
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Usuario|None :
        """ Retorna un usuario a partir del mail con el que se registró. """
        pass

    @abstractmethod
    def get_pendientes(self) -> list[Usuario] :
        """ Retorna los usuarios pendientes de validación """
        pass

    @abstractmethod
    def get_by_id(self, usuario_id: int) -> Usuario:
        """ Obtiene un usuario por su ID """
        pass