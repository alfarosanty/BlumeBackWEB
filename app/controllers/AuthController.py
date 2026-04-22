from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import crear_token_acceso
from app.database import get_db
from app.repositories.imp.UsuarioRepository import UsuarioRepository
from app.schemas.UsuarioSchema import Token
from app.services.imp.AuthService import AuthService

router = APIRouter(tags=["Autenticación"])

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    auth_service = AuthService(UsuarioRepository(db))
    
    # 1. AUTENTICACIÓN (¿Sos quien decís ser?)
    usuario = auth_service.autenticar_usuario(form_data.username, form_data.password)
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # 2. AUTORIZACIÓN (Tomá tu pase libre)
    payload = {
        "sub": usuario.email, 
        "id_cliente": usuario.id_cliente
    }
    
    token = crear_token_acceso(data=payload)
    
    return {"access_token": token, "token_type": "bearer"}