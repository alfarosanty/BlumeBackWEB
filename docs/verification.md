# Verificación — Cómo demostrar que el código funciona

> "El agente no dice que funciona, lo demuestra."

## Niveles de verificación

### N1 — Tests unitarios (pytest)

Cubre lógica aislada (servicios, utilidades) sin base de datos.

```powershell
python -m pytest tests/ -q -m "not integration"
```

Mínimo: camino feliz + ≥1 caso de error por función de servicio.

### N2 — Tests de integración (TestClient + SQLite en memoria)

Cubre endpoints FastAPI completos con DB real (SQLite in-memory como proxy).

```powershell
python -m pytest tests/ -q
```

Fixture estándar para override de DB:

```python
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
client = TestClient(app)
```

Mínimo por endpoint: GET retorna 200 con estructura correcta, auth
requerida retorna 401 sin token.

### N3 — Smoke end-to-end (opcional, manual)

Arrancar la API localmente y verificar manualmente los endpoints nuevos
via `/docs` (Swagger UI de FastAPI).

```powershell
uvicorn app.main:app --reload
# Abrir http://localhost:8000/docs
```

### N4 — Trazabilidad R<n> ↔ test (obligatorio para features SDD)

El implementer documenta en `progress/impl_<name>.md`:

```
R1 → tests/test_catalogo_publico.py::test_get_catalogo_sin_auth_retorna_200
R2 → tests/test_catalogo_publico.py::test_filtro_por_sector
R3 → tests/test_catalogo_publico.py::test_paginacion_correcta
```

El reviewer verifica que cada `R<n>` tenga al menos una entrada.

## Comando de verificación completa

```powershell
.\init.ps1
```

Este comando: (1) verifica archivos del arnés, (2) valida `feature_list.json`,
(3) corre todos los tests. Verde = listo para cerrar sesión.
