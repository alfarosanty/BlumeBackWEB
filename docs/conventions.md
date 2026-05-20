# Convenciones de Desarrollo — Python / FastAPI

## Runtime y herramientas

- Python 3.10+
- FastAPI (última versión compatible)
- SQLAlchemy 2.x con Declarative Base
- Pydantic v2
- `pytest` para tests, `httpx` para cliente en tests de integración
- Activar siempre el venv: `.\venv\Scripts\Activate.ps1`

## Naming

| Elemento | Convención | Ejemplo |
|---|---|---|
| Clases (models, services, repos) | `PascalCase` | `ArticuloMaestro`, `PresupuestoService` |
| Interfaces | `IPascalCase` | `IArticuloService`, `IPresupuestoRepository` |
| Funciones y variables | `snake_case` | `get_paginado`, `articulo_precio_id` |
| Archivos | `PascalCase.py` para clases principales | `ArticuloController.py` |
| Endpoints (URL paths) | `kebab-case` o `snake_case` según FastAPI Router | `/articulos/precios` |
| Constantes | `UPPER_SNAKE_CASE` | `MAX_PAGE_SIZE = 100` |

## Estructura de archivos

- Un archivo por clase/interface principal.
- Los controllers se registran en `main.py` via `app.include_router()`.
- Schemas Pydantic en `app/schemas/` (separar request de response si difieren).
- Usar `PagedResponse[T]` del schema de paginación para todas las listas.

## Pydantic schemas

- Definir `model_config = ConfigDict(from_attributes=True)` en schemas que
  mapeen desde ORM.
- Separar schemas: `XxxCreate`, `XxxUpdate`, `XxxResponse` si los campos
  difieren entre create/update/read.
- Nunca exponer campos sensibles (`password`, `token`) en el response.

## Tests (pytest)

- Un archivo de test por feature SDD: `tests/test_<feature_name>.py`.
- Usar `TestClient` de `fastapi.testclient` para tests de endpoints.
- Fixture de DB: SQLite en memoria con override de `get_db` en `app.dependency_overrides`.
- Cada test lleva un comentario de una línea indicando el `R<n>` que cubre.
- Nomear tests: `test_<accion>_<condicion>` (ej: `test_get_catalogo_sin_auth_retorna_200`).
- Tests independientes entre sí: no depender del estado de otro test.

## Manejo de errores

- Lanzar `HTTPException(status_code=404, detail="...")` cuando un recurso
  no existe.
- Lanzar `HTTPException(status_code=403, detail="...")` para acceso no
  autorizado por rol.
- No exponer stack traces al cliente; loguear internamente si es necesario.
- En operaciones no críticas (ej: envío de email), capturar la excepción
  y continuar sin fallar la operación principal.

## Comentarios

- No comentar qué hace el código (los nombres lo dicen).
- Comentar solo el POR QUÉ: restricciones no obvias, workarounds, invariantes.
- Docstrings en métodos públicos de interfaces y endpoints: una línea máximo.

## Imports

- Orden: stdlib → third-party → local (separados por línea en blanco).
- No usar imports circulares. Si ocurre, revisa la capa: probablemente
  hay lógica de negocio en el lugar equivocado.
