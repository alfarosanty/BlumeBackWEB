"""
Configura SQLite en memoria y stubea dependencias pesadas para todos los tests.
Este archivo es cargado por pytest ANTES de recolectar módulos de test.
"""
import sys
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine as _real_create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ── 1. Stubear dependencias pesadas que se importan a nivel de módulo ────────
_HEAVY_MOCKS = [
    "pandas", "numpy",
    "nltk", "nltk.stem",
    "cloudinary", "cloudinary.uploader",
    "weasyprint", "fontTools", "jinja2",
]
for _mod in _HEAVY_MOCKS:
    sys.modules.setdefault(_mod, MagicMock())

# ── 2. Motor SQLite en memoria con StaticPool ─────────────────────────────────
# StaticPool fuerza una sola conexion compartida: todas las sesiones ven
# las mismas tablas y datos. Sin esto, cada sesion nueva recibe una BD vacia.
_test_engine = _real_create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

# ── 3. Parchear create_engine ANTES de importar app.database ─────────────────
with patch("sqlalchemy.create_engine", return_value=_test_engine):
    import app.database as _db_module  # noqa: E402

_db_module.SessionLocal = _TestSession


def _override_get_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()


_db_module.get_db = _override_get_db
