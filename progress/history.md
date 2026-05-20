# Bitácora histórica (append-only)

> Cada vez que se cierra una sesión, su resumen se añade aquí.
> No edites entradas anteriores. Solo añades al final.

---

## 2026-05-20 — Sesión 0: Montaje del arnés Harness Engineering + SDD

- **Agente:** Claude (setup inicial)
- **Plan:** Montar el arnés completo (CLAUDE.md, AGENTS.md, agents/, docs/, init.ps1, settings.json) adaptado al stack Python/FastAPI del proyecto BlumeWEB Backend.
- **Cambios:** Creados: CLAUDE.md, AGENTS.md, CHECKPOINTS.md, init.ps1, .claude/settings.json, .claude/agents/{leader,spec_author,implementer,reviewer}.md, docs/{architecture,conventions,specs,verification}.md, feature_list.json, progress/{current,history}.md, tests/{__init__,test_smoke}.py.
- **Verificación:** Arnés estructural completo. Tests smoke verdes.
- **Cierre:** Feature backlog definido con 4 features SDD pending. Próximo: feature 1 (catalogo_publico).

---

## 2026-05-20 — Sesión 1: Feature 1 — get_articulos_maestro

- **Agente:** leader → spec_author → implementer
- **Spec aprobado por:** usuario (aprobación explícita)
- **Cambios implementados:**
  - `app/schemas/ApiResponseSchema.py` — `PagedResult[T]` y `ApiResponse[T]`
  - `app/schemas/ArticuloMaestroSchema.py` — DTOs completos con jerarquía
  - `app/models/ArticuloMaestroXArticuloPrecio.py` — relationships `subfamilia` y `articulo_precio`
  - `app/repositories/IArticuloMaestroRepository.py` — interface ABC (3 métodos)
  - `app/repositories/imp/ArticuloMaestroRepository.py` — 3-step batch query (sin N+1)
  - `app/services/IArticuloMaestroService.py` — método abstracto `obtener_paginado`
  - `app/services/imp/ArticuloMaestroService.py` — ensamblado de DTOs
  - `app/controllers/ArticuloController.py` — endpoint `/articulos/maestro` reemplazado (no nuevo archivo)
  - `tests/conftest.py` — SQLite in-memory + StaticPool + heavy module stubs
  - `tests/test_get_articulos_maestro.py` — 9 tests R1-R10
- **Verificación:** 9/9 tests pasan. Sin warnings de overlap.
- **Decisiones clave:** endpoint en ArticuloController.py (no controller separado); replace del endpoint roto (no v2); StaticPool para compartir conexión SQLite en tests.
- **Cierre:** Feature marcada `done`. Próxima: Feature 3 o 4.

---

## 2026-05-20 — Sesión 2: Feature 2 — correccion_get_articulos_maestro

- **Agente:** leader → spec_author → implementer → reviewer
- **Spec aprobado por:** usuario (aprobación explícita tras corrección del filtro `codigo`)
- **Bugs corregidos:**
  - Bug 1: filtro `codigo` usaba `ilike('%x%')` en `ArticuloMaestro.codigo` → devolvía maestros con prefijo común (ej. "CALA" y "CALA/FU"). Corregido a match exacto case-insensitive: `func.lower(ArticuloMaestro.codigo) == codigo.lower()`
  - Bug 2: JOINs de clasificación (sector/familia/subfamilia) en bloques `if` independientes → error SQL cuando solo se pasaba `sector_id` (SubFamilia no estaba en el FROM). Corregido con cadena de JOINs fija en orden: junction → SubFamilia → Familia.
- **Archivos modificados:**
  - `app/repositories/imp/ArticuloMaestroRepository.py` — `_base_stmt` refactorizado
  - `tests/test_correccion_get_articulos_maestro.py` — 7 tests nuevos SQLite in-memory
  - `tests/test_get_articulos_maestro.py` — test de código renombrado para alinearse con el nuevo comportamiento exacto
- **Verificación:** 17 tests pasan, sin regresiones. Reviewer: APROBADO.
- **Cierre:** Feature marcada `done`. Próxima: Feature 3 (notificacion_email_presupuesto).
