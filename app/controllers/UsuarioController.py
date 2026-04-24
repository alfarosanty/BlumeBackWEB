from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import verificar_rol
from app.database import get_db
from app.models.Usuario import Usuario
from app.schemas.UsuarioSchema import RegistroUsuarioEmpresa, UsuarioResponse, EditarUsuarioRequest, UsuarioFiltros
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

ClienteServiceDep = Annotated[ClienteService, Depends(get_cliente_service)]
UsuarioServiceDep = Annotated[UsuarioService, Depends(get_usuario_service)]

@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar(
    datos: RegistroUsuarioEmpresa, 
    usuario_service: UsuarioService = Depends(get_usuario_service)
):
    # Chequeamos si el email ya existe
    if usuario_service.get_by_email(datos.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    if usuario_service.get_by_username(datos.username):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
        
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

@router.get("/pendientes", response_model=list[UsuarioResponse])
def get_pendientes(
    service: UsuarioServiceDep, # <--- ¡Mágicamente ya tenés el servicio listo!
    admin_auth: Usuario = Depends(verificar_rol(["super_admin"]))
):
    # Ya no necesitás crear nada acá adentro. Directo al grano:
    return service.listar_usuarios_pendientes()

@router.patch("/{usuario_id}/configurar", response_model=UsuarioResponse)
def configurar_usuario(
    usuario_id: int,
    datos: EditarUsuarioRequest,
    service: UsuarioServiceDep,
    admin_auth: Usuario = Depends(verificar_rol(["super_admin"]))
):
    try:
        # Esto te sirve tanto para aprobar como para solo cambiar un rol
        return service.editar_usuario_admin(usuario_id, datos)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("", response_model=list[UsuarioResponse])
def get_usuarios_full(
    service: UsuarioServiceDep,
    filtros: UsuarioFiltros = Depends(),
    admin_auth: Usuario = Depends(verificar_rol(["super_admin"]))
):
    # Este endpoint es el motor de la tabla principal del admin
    return service.listar_todos(filtros)