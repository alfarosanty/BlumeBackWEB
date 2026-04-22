from app.core.security import verificar_password
from app.repositories.imp.UsuarioRepository import UsuarioRepository
from typing import cast

class AuthService:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    def autenticar_usuario(self, email: str, password: str):
        usuario = self.usuario_repo.get_by_email(email)
        if not usuario:
            return None
        
        hashed_pass = cast(str, usuario.hashed_password)
        
        if not verificar_password(password, hashed_pass):
            return None
                
        return usuario