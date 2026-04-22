from datetime import datetime, timedelta
import os
from typing import Optional, Union, Any
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# 1. Configuración de Encriptación (Bcrypt)
# Esto es lo que usa la librería passlib que acabás de instalar
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Configuración de JWT
# Cargamos el archivo .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # "login" es la ruta del endpoint


# --- FUNCIONES DE CONTRASEÑA ---

def hash_password(password: str) -> str:
    """Recibe la clave en texto plano y devuelve el hash encriptado."""
    return pwd_context.hash(password)

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una clave en texto plano con el hash de la DB."""
    return pwd_context.verify(plain_password, hashed_password)

# --- FUNCIONES DE TOKEN (JWT) ---

def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un token JWT firmado.
    En 'data' podemos meter el email, id_cliente, etc.
    """
    to_encode = data.copy()
    
    # Calculamos el tiempo de expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY no está configurada en el archivo .env")

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    try:
        if not SECRET_KEY:
            raise ValueError("SECRET_KEY no está configurada en el archivo .env")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str|None = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token no contiene un usuario válido")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")