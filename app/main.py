from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import os
from dotenv import load_dotenv
import cloudinary
# --- PASO CRUCIAL: IMPORTAR TUS MODELOS ---
# Sin estos imports, 'Base.metadata.create_all' no encontrará nada para crear.
# Asegurate de que los nombres coincidan con tus archivos en la carpeta 'models'
from app.models import Articulo, Usuario, Cliente, Presupuesto, CondicionFiscal, Familia, SubFamilia, Medida, Color, ArticuloPrecio, ArticuloPresupuesto, EstadoPresupuesto, Sector
from app.controllers.ArticuloController import router as articulos_router
from app.controllers.UsuarioController import router as usuarios_router
from app.controllers.AuthController import router as auth_router
from app.controllers.PresupuestoController import router as presupuesto_router
from app.controllers.FamiliaController import router as familias_router
from app.controllers.SubFamiliaController import router as subfamilias_router
from app.controllers.SectorController import router as sector_router

# Esta línea busca las tablas en Intermedia. 
# Si NO existen, las crea. Si YA existen, las deja intactas (no borra nada).
Base.metadata.create_all(bind=engine)

load_dotenv()

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
)

app = FastAPI(
    title="Blume API",
    description="Backend para gestión de inventario y facturación textil",
    version="1.0.0"
)

# Configurá los orígenes permitidos
origins = [
    "http://localhost:5173",  # Agregado el puerto de Vite/React
    "http://127.0.0.1:5173",
    # Si vas a publicar tu web, acá agregarías tu dominio real
    # "https://www.blumeweb.com", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Lista de orígenes permitidos
    allow_credentials=True,         # Permitir cookies/sesiones
    allow_methods=["*"],            # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],            # Permitir todos los headers
)

app.include_router(articulos_router)
app.include_router(usuarios_router)
app.include_router(auth_router)
app.include_router(presupuesto_router)
app.include_router(familias_router)
app.include_router(subfamilias_router)
app.include_router(sector_router)



@app.get("/")
def inicio():
    return {
        "mensaje": "Conectado a la nube de Intermedia. ¡Todo listo!",
        "sistema": "Blume ERP",
        "tablas": "Verificadas/Creadas"
    }

# Ejemplo de un endpoint simple para probar en /docs
@app.get("/check")
def check_db():
    return {"status": "ok", "db": "mysql_intermedia"}