# Design — correccion_get_articulos_maestro

Feature ID: 2  
Estado: spec_ready

---

## Archivo a modificar

Un único archivo de producción:

```
app/repositories/imp/ArticuloMaestroRepository.py
```

No se toca el controller, el servicio, los schemas ni ningún modelo.

---

## Diagnóstico detallado

### Bug 1 — filtro `codigo` (línea 61)

```python
# ANTES (incorrecto)
if codigo:
    stmt = stmt.where(ArticuloMaestro.codigo.ilike(f"%{codigo}%"))
```

El filtro usa `ilike` con comodines a ambos lados (`%cala%`). Esto
retorna tanto el maestro `"CALA"` como el maestro `"CALA/FU"` (porque
"CALA/FU" contiene la subcadena "cala"). Con ello, todos los APs de
ambos maestros se cargan y se muestran mezclados.

El criterio de negocio es: el filtro `codigo` debe buscar el maestro
cuyo `codigo` sea exactamente igual al valor proporcionado (match exacto,
case-insensitive). Un usuario que busca `"CALA"` quiere ver solo el
maestro `"CALA"` con todas sus variantes, nunca el maestro `"CALA/FU"`.

### Bug 2 — JOINs condicionales rotos (líneas 43-56)

```python
# ANTES (incorrecto)
if subfamilia_id:
    stmt = stmt.where(ArticuloMaestroXArticuloPrecio.subfamilia_id == subfamilia_id)
if familia_id:
    stmt = stmt.join(SubFamilia, ...).where(SubFamilia.id_familia == familia_id)
if sector_id:
    stmt = stmt.join(Familia, Familia.id == SubFamilia.id_familia).where(...)
```

Si solo `sector_id` está presente: `join_intermedia=True` → se joinea
la tabla intermedia, pero el bloque `if subfamilia_id` no ejecuta y el
bloque `if sector_id` intenta joinear `Familia` usando `SubFamilia.id_familia`
sin que `SubFamilia` esté en el FROM. SQLAlchemy/MySQL lanza un error.

El mismo problema ocurre con `familia_id` solo: se joinea `SubFamilia`
y se filtra por ella, pero el JOIN a `ArticuloMaestroXArticuloPrecio`
solo se hizo si `join_intermedia=True` (correcto en este caso porque
`familia_id` es truthy). Sin embargo, si `sector_id` sola: `SubFamilia`
no está en el FROM cuando se trata de joinear `Familia`.

---

## Solución — pseudocódigo de `_base_stmt` corregido

La estrategia es:

1. Determinar si se necesita alguno de los filtros de clasificación o
   de código (para saber si hay que hacer JOINs extra).
2. Si se filtra por clasificación, añadir los JOINs **siempre en orden
   fijo** (intermedia → SubFamilia → Familia), independientemente de
   qué filtros específicos estén presentes.
3. Si se filtra por `codigo`, añadir el JOIN a `ArticuloPrecio` a través
   de la tabla intermedia y filtrar por `ArticuloPrecio.codigo`.
4. Aplicar los WHERE por separado según los filtros presentes.

```python
from app.models.ArticuloPrecio import ArticuloPrecio  # import nuevo

def _base_stmt(for_count: bool):
    if for_count:
        stmt = select(func.count(func.distinct(ArticuloMaestro.id)))
    else:
        stmt = select(ArticuloMaestro).distinct()

    # --- JOINs de clasificación (orden fijo, siempre juntos) ---
    necesita_clasificacion = any([sector_id, familia_id, subfamilia_id])

    if necesita_clasificacion:
        # 1. Tabla intermedia (siempre base para los filtros de clasificación)
        stmt = stmt.join(
            ArticuloMaestroXArticuloPrecio,
            ArticuloMaestroXArticuloPrecio.articulo_maestro_id == ArticuloMaestro.id,
        )
        # 2. SubFamilia (necesaria para familia_id y sector_id)
        if familia_id or sector_id:
            stmt = stmt.join(
                SubFamilia,
                SubFamilia.id == ArticuloMaestroXArticuloPrecio.subfamilia_id,
            )
            # 3. Familia (necesaria para sector_id)
            if sector_id:
                stmt = stmt.join(
                    Familia,
                    Familia.id == SubFamilia.id_familia,
                )

    # --- WHERE para filtro codigo (match exacto en ArticuloMaestro.codigo) ---
    if codigo:
        stmt = stmt.where(func.lower(ArticuloMaestro.codigo) == codigo.lower())

    # --- WHERE clauses de clasificación ---
    if subfamilia_id:
        stmt = stmt.where(
            ArticuloMaestroXArticuloPrecio.subfamilia_id == subfamilia_id
        )
    if familia_id:
        stmt = stmt.where(SubFamilia.id_familia == familia_id)
    if sector_id:
        stmt = stmt.where(Familia.id_sector == sector_id)

    # --- Filtro activo ---
    if solo_activos is True:
        stmt = stmt.where(ArticuloMaestro.activo == True)  # noqa: E712

    return stmt
```

### Notas de implementación

- No se necesita ningún import nuevo (no se usa `ArticuloPrecio` en el filtro).
- La variable `join_intermedia` del código original puede eliminarse;
  queda reemplazada por `necesita_clasificacion`.
- El filtro `codigo` usa `func.lower()` en ambos lados para garantizar
  case-insensitivity sin depender de la collation de la BD.
- No se cambia la firma de `obtener_paginado` ni ninguna capa superior.
- SQLAlchemy 2.x maneja correctamente JOINs condicionales anidados
  siempre que cada tabla joineada esté en el FROM antes de ser
  referenciada en una condición `ON`.

---

## Alternativa descartada

**Alternativa: filtrar por `ArticuloPrecio.codigo` con ILIKE.**

El spec original proponía unir `ArticuloPrecio` y filtrar por su código.
Se descartó porque el criterio de negocio confirmado es buscar el maestro
por su propio código de forma exacta. Filtrar por el código del AP cambiaría
la semántica del parámetro y requeriría un JOIN innecesario.
