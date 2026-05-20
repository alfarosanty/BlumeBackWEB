"""
Tests de integración para correccion_get_articulos_maestro (Feature 2).
Instancian ArticuloMaestroRepository directamente con una sesión SQLite en memoria.

Mapa de trazabilidad R → test:
  R1 → test_filtro_codigo_exacto_retorna_solo_ese_maestro, test_filtro_codigo_case_insensitive
  R2 → test_filtro_codigo_exacto_retorna_solo_ese_maestro
  R3 → test_filtro_subfamilia_id_solo
  R4 → test_filtro_familia_id_solo
  R5 → test_filtro_sector_id_solo
  R6 → test_filtros_combinados_codigo_y_sector
  R7 → test_sin_filtros_retorna_todos
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# conftest.py ya parcheó app.database antes de la recolección de tests.
# Importamos Base desde app.database para reutilizar el motor SQLite ya creado.
from app.database import Base
from app.models.ArticuloMaestro import ArticuloMaestro
from app.models.ArticuloPrecio import ArticuloPrecio
from app.models.ArticuloMaestroXArticuloPrecio import ArticuloMaestroXArticuloPrecio
from app.models.SubFamilia import SubFamilia
from app.models.Familia import Familia
from app.models.Sector import Sector
from app.repositories.imp.ArticuloMaestroRepository import ArticuloMaestroRepository

# Usamos el motor SQLite ya montado en conftest (StaticPool, en memoria)
from tests.conftest import _test_engine, _override_get_db

# Crear tablas si aún no existen (idempotente)
Base.metadata.create_all(bind=_test_engine)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def limpiar_tablas():
    """Trunca todas las tablas relevantes antes de cada test."""
    db = next(_override_get_db())
    db.query(ArticuloMaestroXArticuloPrecio).delete()
    db.query(ArticuloMaestro).delete()
    db.query(ArticuloPrecio).delete()
    db.query(SubFamilia).delete()
    db.query(Familia).delete()
    db.query(Sector).delete()
    db.commit()
    db.close()


@pytest.fixture()
def db_session():
    """Sesión SQLite aislada para cada test."""
    session = next(_override_get_db())
    yield session
    session.close()


@pytest.fixture()
def repo(db_session):
    """Repositorio instanciado sobre la sesión SQLite."""
    return ArticuloMaestroRepository(db=db_session)


# ---------------------------------------------------------------------------
# Helpers de seeding
# ---------------------------------------------------------------------------

def _seed_clasificacion(db, *, sector_id=1, familia_id=1, subfamilia_id=1):
    """Inserta Sector → Familia → SubFamilia con IDs dados."""
    db.add(Sector(id=sector_id, codigo=f"S{sector_id}", descripcion="Sector", mostrar_en_web=True))
    db.add(Familia(id=familia_id, codigo=f"F{familia_id}", descripcion="Familia", id_sector=sector_id))
    db.add(SubFamilia(id=subfamilia_id, codigo=f"SF{subfamilia_id}", descripcion="SubFamilia", id_familia=familia_id))
    db.flush()


def _seed_maestro_con_ap(db, *, maestro_id, codigo, activo=True,
                          ap_id, subfamilia_id, junction_id=None):
    """Inserta un ArticuloMaestro con su ArticuloPrecio y junction."""
    db.add(ArticuloMaestro(id=maestro_id, codigo=codigo, descripcion=f"Maestro {codigo}", activo=activo))
    db.flush()
    db.add(ArticuloPrecio(id=ap_id, codigo=f"AP{ap_id}", descripcion="Precio",
                          precio1=100.0, precio2=90.0, precio3=80.0, habilitado=True))
    db.flush()
    jid = junction_id if junction_id is not None else ap_id * 100
    db.add(ArticuloMaestroXArticuloPrecio(
        id=jid,
        articulo_maestro_id=maestro_id,
        articulo_precio_id=ap_id,
        subfamilia_id=subfamilia_id,
    ))
    db.flush()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_filtro_codigo_exacto_retorna_solo_ese_maestro(db_session, repo):
    """
    R1, R2: dos maestros "CALA" y "CALA/FU"; buscar "CALA" retorna SOLO
    el maestro "CALA" con todas sus variantes, nunca "CALA/FU".
    """
    _seed_clasificacion(db_session)
    _seed_maestro_con_ap(db_session, maestro_id=1, codigo="CALA", ap_id=1, subfamilia_id=1)
    _seed_maestro_con_ap(db_session, maestro_id=2, codigo="CALA/FU", ap_id=2, subfamilia_id=1)
    db_session.commit()

    total, maestros = repo.obtener_paginado(
        solo_activos=None, codigo="CALA",
        sector_id=None, familia_id=None, subfamilia_id=None,
        skip=0, limit=100,
    )

    assert total == 1, f"Se esperaba 1 maestro, se obtuvieron {total}"
    assert len(maestros) == 1
    assert maestros[0].codigo == "CALA"


def test_filtro_codigo_case_insensitive(db_session, repo):
    """
    R1: buscar "cala" (minúsculas) retorna el maestro "CALA" (mayúsculas).
    """
    _seed_clasificacion(db_session)
    _seed_maestro_con_ap(db_session, maestro_id=3, codigo="CALA", ap_id=3, subfamilia_id=1)
    db_session.commit()

    total, maestros = repo.obtener_paginado(
        solo_activos=None, codigo="cala",
        sector_id=None, familia_id=None, subfamilia_id=None,
        skip=0, limit=100,
    )

    assert total == 1
    assert maestros[0].codigo == "CALA"


def test_filtro_subfamilia_id_solo(db_session, repo):
    """
    R3: filtrar solo por subfamiliaId no lanza excepción y retorna
    solo los maestros vinculados a esa subfamilia.
    """
    _seed_clasificacion(db_session, sector_id=1, familia_id=1, subfamilia_id=1)
    # Segunda subfamilia (diferente)
    db_session.add(SubFamilia(id=2, codigo="SF2", descripcion="SF2", id_familia=1))
    db_session.flush()

    _seed_maestro_con_ap(db_session, maestro_id=4, codigo="M_SF1", ap_id=4, subfamilia_id=1)
    _seed_maestro_con_ap(db_session, maestro_id=5, codigo="M_SF2", ap_id=5, subfamilia_id=2)
    db_session.commit()

    total, maestros = repo.obtener_paginado(
        solo_activos=None, codigo=None,
        sector_id=None, familia_id=None, subfamilia_id=1,
        skip=0, limit=100,
    )

    assert total == 1
    assert maestros[0].codigo == "M_SF1"


def test_filtro_familia_id_solo(db_session, repo):
    """
    R4: filtrar solo por familiaId no lanza excepción y retorna
    solo los maestros cuya subfamilia pertenece a esa familia.
    """
    # Familia 1 con subfamilia 1
    _seed_clasificacion(db_session, sector_id=1, familia_id=1, subfamilia_id=1)
    # Familia 2 con subfamilia 2
    db_session.add(Familia(id=2, codigo="F2", descripcion="Familia2", id_sector=1))
    db_session.flush()
    db_session.add(SubFamilia(id=2, codigo="SF2", descripcion="SF2", id_familia=2))
    db_session.flush()

    _seed_maestro_con_ap(db_session, maestro_id=6, codigo="M_FAM1", ap_id=6, subfamilia_id=1)
    _seed_maestro_con_ap(db_session, maestro_id=7, codigo="M_FAM2", ap_id=7, subfamilia_id=2)
    db_session.commit()

    total, maestros = repo.obtener_paginado(
        solo_activos=None, codigo=None,
        sector_id=None, familia_id=1, subfamilia_id=None,
        skip=0, limit=100,
    )

    assert total == 1
    assert maestros[0].codigo == "M_FAM1"


def test_filtro_sector_id_solo(db_session, repo):
    """
    R5: filtrar solo por sectorId no lanza excepción y retorna
    solo los maestros cuya cadena SubFamilia→Familia pertenece a ese sector.
    """
    # Sector 1 → Familia 1 → SubFamilia 1
    _seed_clasificacion(db_session, sector_id=1, familia_id=1, subfamilia_id=1)
    # Sector 2 → Familia 2 → SubFamilia 2
    db_session.add(Sector(id=2, codigo="S2", descripcion="Sector2", mostrar_en_web=True))
    db_session.flush()
    db_session.add(Familia(id=2, codigo="F2", descripcion="Familia2", id_sector=2))
    db_session.flush()
    db_session.add(SubFamilia(id=2, codigo="SF2", descripcion="SF2", id_familia=2))
    db_session.flush()

    _seed_maestro_con_ap(db_session, maestro_id=8, codigo="M_SEC1", ap_id=8, subfamilia_id=1)
    _seed_maestro_con_ap(db_session, maestro_id=9, codigo="M_SEC2", ap_id=9, subfamilia_id=2)
    db_session.commit()

    total, maestros = repo.obtener_paginado(
        solo_activos=None, codigo=None,
        sector_id=1, familia_id=None, subfamilia_id=None,
        skip=0, limit=100,
    )

    assert total == 1
    assert maestros[0].codigo == "M_SEC1"


def test_filtros_combinados_codigo_y_sector(db_session, repo):
    """
    R6: combinar codigo y sectorId aplica ambos (AND) y retorna solo
    los maestros que cumplen ambos criterios.
    """
    # Sector 1 → Familia 1 → SubFamilia 1
    _seed_clasificacion(db_session, sector_id=1, familia_id=1, subfamilia_id=1)
    # Sector 2 → Familia 2 → SubFamilia 2
    db_session.add(Sector(id=2, codigo="S2", descripcion="Sector2", mostrar_en_web=True))
    db_session.flush()
    db_session.add(Familia(id=2, codigo="F2", descripcion="Familia2", id_sector=2))
    db_session.flush()
    db_session.add(SubFamilia(id=2, codigo="SF2", descripcion="SF2", id_familia=2))
    db_session.flush()

    # "CALA" en sector 1 (debe aparecer)
    _seed_maestro_con_ap(db_session, maestro_id=10, codigo="CALA", ap_id=10, subfamilia_id=1)
    # "CALA" en sector 2 (no debe aparecer porque sector ≠ 1)
    _seed_maestro_con_ap(db_session, maestro_id=11, codigo="CALA",
                          ap_id=11, subfamilia_id=2, junction_id=1100)
    # "OTRO" en sector 1 (no debe aparecer porque codigo ≠ "CALA")
    _seed_maestro_con_ap(db_session, maestro_id=12, codigo="OTRO", ap_id=12, subfamilia_id=1)
    db_session.commit()

    total, maestros = repo.obtener_paginado(
        solo_activos=None, codigo="CALA",
        sector_id=1, familia_id=None, subfamilia_id=None,
        skip=0, limit=100,
    )

    assert total == 1
    assert maestros[0].id == 10


def test_sin_filtros_retorna_todos(db_session, repo):
    """
    R7: sin ningún filtro, se retornan todos los maestros sin restricción.
    """
    _seed_clasificacion(db_session)
    _seed_maestro_con_ap(db_session, maestro_id=13, codigo="X1", ap_id=13, subfamilia_id=1)
    _seed_maestro_con_ap(db_session, maestro_id=14, codigo="X2", ap_id=14, subfamilia_id=1)
    # Maestro sin junction (no tiene clasificación)
    db_session.add(ArticuloMaestro(id=15, codigo="X3", descripcion="Sin clasificacion", activo=True))
    db_session.commit()

    total, maestros = repo.obtener_paginado(
        solo_activos=None, codigo=None,
        sector_id=None, familia_id=None, subfamilia_id=None,
        skip=0, limit=100,
    )

    assert total == 3
    codigos = {m.codigo for m in maestros}
    assert codigos == {"X1", "X2", "X3"}
