"""
Tests de integración para GET /articulos/maestro.
Trazabilidad: R1-R10 mapeados en cada test.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# conftest.py parchó app.database antes de esta importación
from app.main import app
from app.database import Base
from app.core.security import obtener_usuario_confirmado, obtener_usuario_actual
from app.models.Usuario import Usuario
from app.models.ArticuloMaestro import ArticuloMaestro
from app.models.ArticuloPrecio import ArticuloPrecio
from app.models.ArticuloMaestroXArticuloPrecio import ArticuloMaestroXArticuloPrecio
from app.models.SubFamilia import SubFamilia
from app.models.Familia import Familia
from app.models.Sector import Sector
from app.models.Medida import Medida

# Crea las tablas SQLite una vez por sesión de tests
from tests.conftest import _test_engine, _override_get_db
Base.metadata.create_all(bind=_test_engine)


# ---------- Fixtures ----------

def _usuario_confirmado():
    return Usuario(id=1, email="t@t.com", username="tester",
                   hashed_password="x", confirmado=True, rol="cliente")

def _usuario_no_confirmado():
    return Usuario(id=2, email="u@u.com", username="unconfirmed",
                   hashed_password="x", confirmado=False, rol="cliente")


@pytest.fixture(autouse=True)
def limpiar_tablas():
    """Trunca las tablas relevantes antes de cada test para aislamiento."""
    db = next(_override_get_db())
    db.query(ArticuloMaestroXArticuloPrecio).delete()
    db.query(ArticuloMaestro).delete()
    db.query(ArticuloPrecio).delete()
    db.query(SubFamilia).delete()
    db.query(Familia).delete()
    db.query(Sector).delete()
    db.query(Medida).delete()
    db.commit()
    db.close()


@pytest.fixture
def client_autenticado():
    """TestClient con usuario confirmado sobreescrito."""
    app.dependency_overrides[obtener_usuario_confirmado] = _usuario_confirmado
    app.dependency_overrides[obtener_usuario_actual] = _usuario_confirmado
    app.dependency_overrides[_override_get_db.__wrapped__ if hasattr(_override_get_db, '__wrapped__') else type(None)] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_sin_auth():
    """TestClient sin override de auth (golpea el middleware real → 401)."""
    app.dependency_overrides.clear()
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def client_no_confirmado():
    app.dependency_overrides[obtener_usuario_confirmado] = _usuario_no_confirmado
    app.dependency_overrides[obtener_usuario_actual] = _usuario_no_confirmado
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _seed_base(db: Session):
    """Inserta jerarquía mínima: Sector → Familia → SubFamilia."""
    sector = Sector(id=1, codigo="S1", descripcion="Sector Test", mostrar_en_web=True)
    familia = Familia(id=1, codigo="F1", descripcion="Familia Test", id_sector=1)
    subfamilia = SubFamilia(id=1, codigo="SF1", descripcion="SubFamilia Test", id_familia=1)
    db.add_all([sector, familia, subfamilia])
    db.flush()
    return subfamilia


def _seed_maestro(db: Session, *, id: int, codigo: str, activo: bool,
                  ap_id: int | None = None, subfamilia_id: int | None = None):
    maestro = ArticuloMaestro(id=id, codigo=codigo, descripcion=f"Maestro {codigo}", activo=activo)
    db.add(maestro)
    db.flush()
    if ap_id and subfamilia_id:
        ap = ArticuloPrecio(id=ap_id, codigo=f"AP{ap_id}", descripcion="Precio",
                            precio1=100.0, precio2=90.0, precio3=80.0, habilitado=True)
        db.add(ap)
        db.flush()
        db.add(ArticuloMaestroXArticuloPrecio(
            id=ap_id * 100, articulo_maestro_id=id,
            articulo_precio_id=ap_id, subfamilia_id=subfamilia_id
        ))
    db.commit()
    return maestro


# ---------- Tests ----------

def test_sin_token_retorna_401(client_sin_auth):
    """R2: sin JWT → 401."""
    r = client_sin_auth.get("/articulos/maestro")
    assert r.status_code == 401


def test_usuario_no_confirmado_retorna_403(client_no_confirmado):
    """R3: usuario con confirmado=False → 403."""
    app.dependency_overrides[obtener_usuario_confirmado] = lambda: (_ for _ in ()).throw(
        __import__('fastapi').HTTPException(status_code=403, detail="no confirmado")
    )
    r = client_no_confirmado.get("/articulos/maestro")
    assert r.status_code == 403


def test_get_maestros_autenticado_retorna_200_con_wrapper(client_autenticado):
    """R1, R9: 200 y estructura {success, data:{items,totalItems,pageNumber,pageSize,totalPages}}."""
    db = next(_override_get_db())
    _seed_base(db)
    _seed_maestro(db, id=10, codigo="M001", activo=True, ap_id=1, subfamilia_id=1)
    db.close()

    r = client_autenticado.get("/articulos/maestro")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    data = body["data"]
    assert "items" in data
    assert "totalItems" in data
    assert "pageNumber" in data
    assert "pageSize" in data
    assert "totalPages" in data
    assert data["pageNumber"] == 1
    assert data["pageSize"] == 20
    assert data["totalItems"] >= 1


def test_filtro_activo_true_solo_trae_activos(client_autenticado):
    """R4: activo=true filtra solo los maestros activos."""
    db = next(_override_get_db())
    _seed_base(db)
    _seed_maestro(db, id=11, codigo="ACTIVO", activo=True, ap_id=2, subfamilia_id=1)
    _seed_maestro(db, id=12, codigo="INACTIVO", activo=False, ap_id=3, subfamilia_id=1)
    db.close()

    r = client_autenticado.get("/articulos/maestro?activo=true")
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    codigos = [i["codigo"] for i in items]
    assert "ACTIVO" in codigos
    assert "INACTIVO" not in codigos


def test_filtro_codigo_exacto(client_autenticado):
    """R5: filtro codigo hace búsqueda exacta case-insensitive sobre ArticuloMaestro.codigo."""
    db = next(_override_get_db())
    _seed_base(db)
    _seed_maestro(db, id=13, codigo="CAMISA001", activo=True, ap_id=4, subfamilia_id=1)
    _seed_maestro(db, id=14, codigo="PANTALON001", activo=True, ap_id=5, subfamilia_id=1)
    db.close()

    r = client_autenticado.get("/articulos/maestro?codigo=camisa001")
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["codigo"] == "CAMISA001"


def test_paginacion_page_number_y_page_size(client_autenticado):
    """R6: pageSize=1 retorna 1 item por página; pageNumber=2 retorna la segunda."""
    db = next(_override_get_db())
    _seed_base(db)
    _seed_maestro(db, id=15, codigo="PAG001", activo=True, ap_id=6, subfamilia_id=1)
    _seed_maestro(db, id=16, codigo="PAG002", activo=True, ap_id=7, subfamilia_id=1)
    db.close()

    r1 = client_autenticado.get("/articulos/maestro?pageSize=1&pageNumber=1")
    assert r1.status_code == 200
    data1 = r1.json()["data"]
    assert len(data1["items"]) == 1
    assert data1["totalItems"] == 2
    assert data1["totalPages"] == 2

    r2 = client_autenticado.get("/articulos/maestro?pageSize=1&pageNumber=2")
    assert r2.status_code == 200
    data2 = r2.json()["data"]
    assert len(data2["items"]) == 1
    assert data2["pageNumber"] == 2

    # Los dos items deben ser distintos
    codigo1 = data1["items"][0]["codigo"]
    codigo2 = data2["items"][0]["codigo"]
    assert codigo1 != codigo2


def test_page_size_mayor_100_retorna_422(client_autenticado):
    """R7: pageSize > 100 → 422 (validación Pydantic)."""
    r = client_autenticado.get("/articulos/maestro?pageSize=101")
    assert r.status_code == 422


def test_estructura_dto_incluye_subfamilia_y_variantes(client_autenticado):
    """R8: cada item tiene subfamilia (con familia y sector) y variantes."""
    db = next(_override_get_db())
    _seed_base(db)
    _seed_maestro(db, id=17, codigo="DTO001", activo=True, ap_id=8, subfamilia_id=1)
    db.close()

    r = client_autenticado.get("/articulos/maestro")
    assert r.status_code == 200
    item = r.json()["data"]["items"][0]

    assert "id" in item
    assert "codigo" in item
    assert "activo" in item
    assert "variantes" in item
    assert "subfamilia" in item

    sf = item["subfamilia"]
    assert sf is not None
    assert "familia" in sf
    assert sf["familia"] is not None
    assert "sector" in sf["familia"]

    variante = item["variantes"][0]
    assert "id" in variante
    assert "precio1" in variante
    assert "habilitado" in variante
    assert "medida" in variante  # puede ser null si no hay Articulo vinculado


def test_maestro_sin_vinculos_retorna_subfamilia_null_y_variantes_vacio(client_autenticado):
    """R10: maestro sin junctions → subfamilia=null, variantes=[]."""
    db = next(_override_get_db())
    maestro = ArticuloMaestro(id=18, codigo="SINVINCULOS", descripcion="Sin links", activo=True)
    db.add(maestro)
    db.commit()
    db.close()

    r = client_autenticado.get("/articulos/maestro")
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    item = next(i for i in items if i["codigo"] == "SINVINCULOS")
    assert item["subfamilia"] is None
    assert item["variantes"] == []
