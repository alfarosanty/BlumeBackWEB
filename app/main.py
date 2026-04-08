from fastapi import FastAPI
from app.database import engine, Base

# --- PASO CRUCIAL: IMPORTAR TUS MODELOS ---
# Sin estos imports, 'Base.metadata.create_all' no encontrará nada para crear.
# Asegurate de que los nombres coincidan con tus archivos en la carpeta 'models'
from app.models import Articulo, Usuario, Cliente, Presupuesto, CondicionFiscal, Familia, SubFamilia, Medida, Color, ArticuloPrecio, ArticuloPresupuesto, EstadoPresupuesto 

# Esta línea busca las tablas en Intermedia. 
# Si NO existen, las crea. Si YA existen, las deja intactas (no borra nada).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Blume API",
    description="Backend para gestión de inventario y facturación textil",
    version="1.0.0"
)

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