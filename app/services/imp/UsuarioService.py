from sqlalchemy import cast

from app.repositories.imp.UsuarioRepository import UsuarioRepository
from app.schemas.UsuarioSchema import RegistroUsuarioEmpresa, EditarUsuarioRequest, UsuarioFiltros
from app.models.Usuario import Usuario
from app.core.security import hash_password
from app.services.IUsuarioService import IUsuarioService
from app.services.imp.ClienteService import ClienteService # La función que armamos antes

class UsuarioService(IUsuarioService):
    def __init__(self, usuario_repository: UsuarioRepository, cliente_service:ClienteService):
        self.usuario_repo = usuario_repository
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
            username=datos.username,
            hashed_password=hash_password(datos.password),
            id_cliente=cliente_db.id,
            confirmado=False
        )
        
        return self.usuario_repo.create(nuevo_usuario)
    
    def get_by_email(self, email: str):

        return self.usuario_repo.get_by_email(email)
    
    def get_by_username(self, username: str):

        return self.usuario_repo.get_by_username(username)

    def crear_usuario(self, usuario_data: RegistroUsuarioEmpresa) -> Usuario:
        raise NotImplementedError
    
    def listar_usuarios_pendientes(self):
        return self.usuario_repo.get_pendientes()
    
    def editar_usuario_admin(self, usuario_id: int, datos: EditarUsuarioRequest):
        usuario = self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            raise Exception("Usuario no encontrado")
        
        if datos.rol is not None:
            usuario.rol = datos.rol # type: ignore
            
        if datos.confirmado is not None:
            usuario.confirmado = datos.confirmado # type: ignore

        if datos.id_cliente_asociado is not None:
            if usuario.cliente:
                usuario.cliente.id_cliente_local = datos.id_cliente_asociado # type: ignore
            else:
                raise Exception("Este usuario no tiene un perfil de cliente asociado")

        self.usuario_repo.commit_changes()
        return usuario
    
    def listar_todos(self, filtros: UsuarioFiltros):
        return self.usuario_repo.get_todos_con_filtros(filtros)
    
    def dar_de_baja_logica(self, usuario_id: int):
        usuario = self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            raise Exception("Usuario no encontrado")
        
        # En lugar de eliminar, desactivamos
        usuario.is_active = False # type: ignore
        
        self.usuario_repo.commit_changes()
        return True

    
