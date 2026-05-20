# Tasks — correccion_get_articulos_maestro

Feature ID: 2  
Estado: spec_ready

---

- [x] T1 — Reestructurar los JOINs de clasificación en `_base_stmt`:
  reemplazar los bloques `if` independientes por la cadena fija
  intermedia → SubFamilia (condicional) → Familia (condicional), según
  el pseudocódigo de `design.md`. Eliminar la variable `join_intermedia`.
  Cubre: R3, R4, R5, R6, R7.

- [x] T2 — Corregir el filtro `codigo` en `_base_stmt`: reemplazar el
  `ilike(f"%{codigo}%")` sobre `ArticuloMaestro.codigo` por una
  comparación exacta case-insensitive: `func.lower(ArticuloMaestro.codigo) == codigo.lower()`.
  Cubre: R1, R2, R6.

- [x] T3 — Escribir tests en `tests/test_correccion_get_articulos_maestro.py`
  con SQLite en memoria:
  - `test_filtro_codigo_exacto_retorna_solo_ese_maestro` — dos maestros
    con códigos "CALA" y "CALA/FU"; buscar por "CALA" retorna solo el
    maestro "CALA" con todas sus variantes. Cubre: R1, R2.
  - `test_filtro_codigo_case_insensitive` — buscar "cala" retorna el
    maestro "CALA". Cubre: R1.
  - `test_filtro_subfamilia_id_solo` — filtrar solo por subfamiliaId
    no lanza excepción y retorna los maestros correctos. Cubre: R3.
  - `test_filtro_familia_id_solo` — filtrar solo por familiaId no lanza
    excepción y retorna los maestros correctos. Cubre: R4.
  - `test_filtro_sector_id_solo` — filtrar solo por sectorId no lanza
    excepción y retorna los maestros correctos. Cubre: R5.
  - `test_filtros_combinados_codigo_y_sector` — combinar `codigo` y
    `sectorId` retorna solo los maestros que cumplen ambos. Cubre: R6.
  - `test_sin_filtros_retorna_todos` — sin filtros retorna todos los
    maestros de la fixture. Cubre: R7.
  Cubre: R1, R2, R3, R4, R5, R6, R7.

- [x] T4 — Ejecutar `.\init.ps1` y confirmar que todos los tests nuevos
  pasan en verde y que no hay regresiones en la suite existente.
  Cubre: R1, R2, R3, R4, R5, R6, R7.
