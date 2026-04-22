from abc import ABC, abstractmethod

from app.models.Usuario import Usuario
from app.schemas.UsuarioSchema import RegistroUsuarioEmpresa


class IUsuarioService(ABC):

    @abstractmethod
    def crear_usuario_y_cliente(self, datos: RegistroUsuarioEmpresa) -> Usuario:
        """ Creación de usuario a partir de datos recibidos. """
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Usuario|None:
        """ Obtención de usuario a partir de su mail. """
        pass
