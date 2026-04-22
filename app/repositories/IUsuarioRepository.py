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