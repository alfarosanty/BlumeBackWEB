from app.core.security import verificar_password
from app.repositories.imp.UsuarioRepository import UsuarioRepository
from typing import cast

class AuthService:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    def autenticar_usuario(self, email: str, password_plano: str):
        # 1. Buscamos al usuario por email
        usuario = self.usuario_repo.get_by_email(email)
        if not usuario:
            return None
        
        # 2. Verificamos la contraseña hasheada
        if not verificar_password(password_plano, str(usuario.hashed_password)):
            return None
            
        return usuario