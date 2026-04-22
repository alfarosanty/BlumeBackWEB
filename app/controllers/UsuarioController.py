from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.UsuarioSchema import RegistroUsuarioEmpresa, UsuarioResponse
from app.repositories.imp.UsuarioRepository import UsuarioRepository
from app.repositories.imp.ClienteRepository import ClienteRepository
from app.services.imp.UsuarioService import UsuarioService
from app.services.imp.ClienteService import ClienteService
from fastapi import status

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def get_cliente_service(db: Session = Depends(get_db)):
    repo = ClienteRepository(db)
    return ClienteService(repo)

def get_usuario_service(db: Session = Depends(get_db), 
                        cliente_service: ClienteService = Depends(get_cliente_service)):
    repo = UsuarioRepository(db)
    return UsuarioService(repo, cliente_service)


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar(
    datos: RegistroUsuarioEmpresa, 
    usuario_service: UsuarioService = Depends(get_usuario_service)
):
    # Chequeamos si el email ya existe
    if usuario_service.get_by_email(datos.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")
        
    return usuario_service.crear_usuario_y_cliente(datos)
# 2. ENDPOINT PARA BUSCAR POR EMAIL (GET)
@router.get("/{email}", response_model=UsuarioResponse)
def obtener_usuario_por_email(
    email: str, 
    service: UsuarioService = Depends(get_usuario_service)
):
    usuario = service.get_by_email(email)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario