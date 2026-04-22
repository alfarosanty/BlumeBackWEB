from sqlalchemy.orm import Session
from app.models.Usuario import Usuario
from app.repositories.IUsuarioRepository import IUsuarioRepository

class UsuarioRepository(IUsuarioRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, usuario: Usuario):
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def get_by_email(self, email: str):
        return self.db.query(Usuario).filter(Usuario.email == email).first()