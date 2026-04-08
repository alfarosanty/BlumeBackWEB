import urllib.parse  # Para limpiar la contraseña
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

# Leemos los datos de tu .env
DB_USER = config("DB_USER")
DB_PASS = config("DB_PASSWORD")
DB_HOST = config("DB_HOST")
DB_NAME = config("DB_NAME")

# --- EL CAMBIO CLAVE AQUÍ ---
# Escapamos los caracteres especiales de la contraseña (como , * {)
DB_PASS_SAFE = urllib.parse.quote_plus(str(DB_PASS))

# Usamos la contraseña "limpia" en la URL
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS_SAFE}@{DB_HOST}/{DB_NAME}"
# ----------------------------

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()