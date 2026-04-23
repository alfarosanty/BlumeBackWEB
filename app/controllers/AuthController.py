from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import crear_token_acceso
from app.services.imp.AuthService import AuthService
from app.repositories.imp.UsuarioRepository import UsuarioRepository
from app.schemas.UsuarioSchema import Token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    service = AuthService(UsuarioRepository(db))
    
    # Intentamos autenticar
    usuario = service.autenticar_usuario(form_data.username, form_data.password)
    
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


    # Creamos el "Pase Libre" (Token) por 8 horas
    # Metemos id_cliente para que Angular sepa de qué empresa es
    token_data = {
        "sub": usuario.email,
        "id_cliente": usuario.id_cliente,
        "rol": usuario.rol,
        "username": usuario.username
    }
    
    access_token = crear_token_acceso(data=token_data)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }