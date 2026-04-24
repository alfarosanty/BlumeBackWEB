from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class UsuarioBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    rol: str
    id_cliente: Optional[int] = None
    is_active: bool = True

class UsuarioResponse(UsuarioBase):
    id: int
    fecha_creacion: datetime

class Config:
    from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UsuarioResponse

class TokenData(BaseModel):
    email: Optional[str] = None
    id_cliente: Optional[int] = None

class RegistroUsuarioEmpresa(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8)
    
    razon_social: str = Field(..., min_length=3, max_length=150)
    cuit: str = Field(..., pattern=r"^\d+$", min_length=11, max_length=11)
    telefono: Optional[str] = Field(None, pattern=r"^\d+$")

    @field_validator('password')
    @classmethod
    def validar_password_fuerte(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError('La contraseña debe tener al menos una letra mayúscula')
        if not re.search(r"\d", v):
            raise ValueError('La contraseña debe tener al menos un número')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('La contraseña debe tener al menos un carácter especial')
        return v

    @field_validator('cuit')
    @classmethod
    def validar_cuit_numerico(cls, v: str) -> str:
        if len(v) != 11:
            raise ValueError('El CUIT debe tener exactamente 11 dígitos')
        return v
    

class EditarUsuarioRequest(BaseModel):
    rol: Optional[str] = None
    id_cliente_asociado: Optional[int] = None 
    confirmado: Optional[bool] = None

class UsuarioFiltros(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    rol: Optional[str] = None
    confirmado: Optional[bool] = None
