from app.repositories.imp.UsuarioRepository import UsuarioRepository
from app.schemas.UsuarioSchema import RegistroUsuarioEmpresa
from app.models.Usuario import Usuario
from app.core.security import hash_password
from app.services.IUsuarioService import IUsuarioService
from app.services.imp.ClienteService import ClienteService # La función que armamos antes

class UsuarioService(IUsuarioService):
    def __init__(self, usuario_repository: UsuarioRepository, cliente_service:ClienteService):
        self.repo = usuario_repository
        self.cliente_service = cliente_service

    def crear_usuario_y_cliente(self, datos: RegistroUsuarioEmpresa):
        # 1. Creamos el Cliente primero
        cliente_db = self.cliente_service.crear(
            razon_social=datos.razon_social,
            cuit=datos.cuit,
            telefono=datos.telefono # type: ignore
        )

        # 2. Creamos el Usuario vinculado a ese Cliente
        nuevo_usuario = Usuario(
            email=datos.email,
            hashed_password=hash_password(datos.password),
            id_cliente=cliente_db.id,
            confirmado=False
        )
        
        return self.repo.create(nuevo_usuario)
    
    def get_by_email(self, email: str):

        return self.repo.get_by_email(email)

    def crear_usuario(self, usuario_data: RegistroUsuarioEmpresa) -> Usuario:
        raise NotImplementedError

    
