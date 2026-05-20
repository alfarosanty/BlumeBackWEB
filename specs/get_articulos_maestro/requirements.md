# Requirements — get_articulos_maestro

> Notación EARS estricta. Cada R<n> es verificable por ≥1 test pytest.

---

## R1 — Endpoint accesible
El sistema DEBE exponer el endpoint `GET /articulos/maestro` que retorna una lista paginada de ArticuloMaestro con el wrapper `ApiResponse[PagedResult[ArticuloMaestroDto]]`.

## R2 — Autenticación obligatoria
CUANDO el request a `GET /articulos/maestro` no incluye un JWT válido en el header `Authorization: Bearer <token>`, el sistema DEBE retornar HTTP 401.

## R3 — Usuario confirmado
CUANDO el usuario autenticado tiene el campo `confirmado = False`, el sistema DEBE retornar HTTP 403.

## R4 — Filtro por activo
CUANDO el query param `activo=true` es enviado, el sistema DEBE retornar únicamente ArticuloMaestro con `activo = True`.
CUANDO `activo` no se envía o se envía `activo=false`, el sistema DEBE retornar todos los ArticuloMaestro sin filtrar por ese campo.

## R5 — Filtros acumulables
El sistema DEBE soportar los siguientes filtros opcionales acumulables (AND):
- `codigo`: filtra ArticuloMaestro cuyo campo `codigo` contenga el valor (case-insensitive, ilike).
- `sectorId`: filtra por ID del Sector asociado vía la tabla de vinculación.
- `familiaId`: filtra por ID de la Familia asociada vía la tabla de vinculación.
- `subfamiliaId`: filtra por ID de la SubFamilia de la tabla de vinculación.

## R6 — Paginación
El sistema DEBE soportar paginación mediante los query params:
- `pageNumber` (entero, default 1, mínimo 1)
- `pageSize` (entero, default 20, mínimo 1, máximo 100)

## R7 — Validación de paginación
SI `pageNumber < 1` o `pageSize < 1` o `pageSize > 100` ENTONCES el sistema DEBE retornar HTTP 422 con mensajes de validación descriptivos (FastAPI Pydantic validation error estándar).

## R8 — Estructura de cada ArticuloMaestroDto
El sistema DEBE retornar cada ArticuloMaestro con la siguiente estructura completa:
- Datos base: `id`, `codigo`, `descripcion`, `url_foto`, `activo`.
- `subfamilia`: datos de la SubFamilia del **primer** vínculo en `ArticuloMaestroXArticuloPrecio`, incluyendo su `Familia` y el `Sector` de esa Familia. `null` si no hay vínculos.
- `variantes`: lista de todos los `ArticuloPrecio` vinculados, cada uno incluyendo `id`, `codigo`, `descripcion`, `precio1`, `precio2`, `precio3`, `habilitado` y la `medida` (del primer `Articulo` que apunte a ese `ArticuloPrecio`). La medida es `null` si no existe ningún `Articulo` vinculado al AP.

## R9 — Wrapper de respuesta
El sistema DEBE envolver la respuesta en la estructura:
```json
{
  "success": true,
  "data": {
    "items": [...],
    "totalItems": 100,
    "pageNumber": 1,
    "pageSize": 20,
    "totalPages": 5
  },
  "message": null
}
```
Donde `data` es de tipo `PagedResult[ArticuloMaestroDto]`.

## R10 — Maestro sin vínculos
El sistema DEBE retornar un ArticuloMaestro que no tenga vinculaciones en `ArticuloMaestroXArticuloPrecio` con `subfamilia: null` y `variantes: []`.
