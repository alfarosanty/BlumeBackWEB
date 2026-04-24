from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import crear_token_acceso, obtener_usuario_actual
from app.models.Usuario import Usuario
from app.services.imp.AuthService import AuthService
from app.repositories.imp.UsuarioRepository import UsuarioRepository
from app.schemas.UsuarioSchema import Token, UsuarioResponse


router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    authService = AuthService(UsuarioRepository(db))
    
    usuario = authService.autenticar_usuario(form_data.username, form_data.password)
    
    if not usuario:
        raise HTTPException(
            status_code=401, 
            detail="Email o contraseña incorrectos"
        )
    
    if not usuario.is_active: # type: ignore
        raise HTTPException(
            status_code=401, 
            detail="Esta cuenta ha sido desactivada. Contacte al administrador."
        )

    token_data = {
        "sub": usuario.email,
        "id_cliente": usuario.id_cliente,
        "rol": usuario.rol,
        "username": usuario.username
    }
    
    access_token = crear_token_acceso(data=token_data)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": usuario
    }

@router.get("/validar-token", response_model=UsuarioResponse)
def verificar_token(
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Retorna los datos del usuario si el token en el header es válido.
    """
    return usuario_actual