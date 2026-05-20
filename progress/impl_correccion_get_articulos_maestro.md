# Implementacion — correccion_get_articulos_maestro

Feature ID: 2
Fecha: 2026-05-20

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `app/repositories/imp/ArticuloMaestroRepository.py` | T1: JOINs orden fijo, elimina `join_intermedia`. T2: filtro `codigo` exacto con `func.lower()`. |
| `tests/test_get_articulos_maestro.py` | Actualiza `test_filtro_codigo_ilike` → `test_filtro_codigo_exacto` (match exacto, no subcadena). |
| `tests/test_correccion_get_articulos_maestro.py` | 7 tests nuevos con SQLite en memoria. |

## Resultado pytest

```
17 passed, 7 warnings in 1.69s
```

Suite completa verde. Sin regresiones.

## Mapa R → test

| Requisito | Test(s) |
|-----------|---------|
| R1 | test_filtro_codigo_exacto_retorna_solo_ese_maestro, test_filtro_codigo_case_insensitive |
| R2 | test_filtro_codigo_exacto_retorna_solo_ese_maestro |
| R3 | test_filtro_subfamilia_id_solo |
| R4 | test_filtro_familia_id_solo |
| R5 | test_filtro_sector_id_solo |
| R6 | test_filtros_combinados_codigo_y_sector |
| R7 | test_sin_filtros_retorna_todos |
