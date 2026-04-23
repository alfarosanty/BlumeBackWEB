from sqlalchemy.orm import Session, joinedload
from app.models.Usuario import Usuario
from app.repositories.IUsuarioRepository import IUsuarioRepository
from app.schemas.UsuarioSchema import UsuarioFiltros

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
    
    def get_by_username(self, username: str):
        return self.db.query(Usuario).filter(Usuario.username == username).first()
    
    def get_pendientes(self) -> list[Usuario]:
        return self.db.query(Usuario).filter(Usuario.confirmado == False).all()
    
    def get_by_id(self, usuario_id: int) -> Usuario:
        return (
            self.db.query(Usuario)
            .options(joinedload(Usuario.cliente)) # Esto hace un JOIN y trae todo junto
            .filter(Usuario.id == usuario_id)
            .first()
        )

    def commit_changes(self):
        self.db.commit()

    def get_todos_con_filtros(self, filtros: UsuarioFiltros) -> list[Usuario]:
        query = self.db.query(Usuario).options(joinedload(Usuario.cliente))
        
        if filtros.email:
            query = query.filter(Usuario.email.contains(filtros.email))
        if filtros.username:
            query = query.filter(Usuario.username.contains(filtros.username))
        if filtros.rol:
            query = query.filter(Usuario.rol == filtros.rol)
        if filtros.confirmado is not None:
            query = query.filter(Usuario.confirmado == filtros.confirmado)
            
        return query.all()