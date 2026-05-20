# Spec Driven Development (SDD)

> Flujo Kiro-style: requirements → design → tasks → code. El código no se
> escribe hasta que el spec está aprobado por un humano.

## Estructura

Cada feature `"sdd": true` tiene `specs/<feature-name>/` con:
`requirements.md` (QUÉ, EARS), `design.md` (CÓMO), `tasks.md` (PASOS).
`<feature-name>` = campo `name` de `feature_list.json`.

## Estados

```
pending → [spec_author] → spec_ready → ⏸ HUMANO → in_progress →
[implementer → reviewer] → done
```

## La puerta de aprobación humana

El flujo se detiene **una vez**: cuando `spec_author` termina los 3
archivos, marca `spec_ready` y para. El humano lee `specs/<feature>/` y
dice "aprobado" (o pide cambios). Solo entonces el leader hace
`spec_ready → in_progress`.

## requirements.md — EARS estricto

Cada requirement es un párrafo numerado (`R1`, `R2`, ...) con uno de:

| Patrón | Plantilla |
|---|---|
| Ubicuo | `El sistema DEBE <acción>.` |
| Evento | `CUANDO <disparador>, el sistema DEBE <acción>.` |
| Estado | `MIENTRAS <estado>, el sistema DEBE <acción>.` |
| Opcional | `DONDE <feature opcional>, el sistema DEBE <acción>.` |
| No deseado | `SI <evento no deseado> ENTONCES el sistema DEBE <acción>.` |

Reglas: id estable; cada `R<n>` verificable por ≥1 test pytest; no
mezclar varios `DEBE`; solo `DEBE`/`NO DEBE` (nada de "podría", "soporta").

## design.md — decisiones técnicas

Antes de tocar código: archivos a crear/modificar, schemas Pydantic nuevos,
funciones/métodos de servicio, y **mínimo una alternativa descartada con su
porqué**. Apóyate en `architecture.md`/`conventions.md`; documenta solo
dónde la feature roza la frontera de esas reglas.

## tasks.md — checklist ejecutable

Pasos discretos en orden, cada uno con checkbox y los `R<n>` que cubre.
Ejemplo:
- [ ] T1 — Añadir schema `CatalogoResponse`. Cubre: R1.
- [ ] T2 — Implementar `ICatalogoService.get_catalogo()`. Cubre: R2.
- [ ] T3 — Implementar `CatalogoService.get_catalogo()`. Cubre: R2.
- [ ] T4 — Crear endpoint GET `/catalogo`. Cubre: R1, R2.
- [ ] T5 — Test del endpoint sin auth. Cubre: R3.

El implementer marca `[x]`. El reviewer rechaza si queda `[ ]` sin
justificación.

## Trazabilidad (regla dura)

Cada test mapea a un `R<n>`; cada `R<n>` tiene ≥1 test. El reviewer lo
comprueba. El implementer documenta el mapa en `progress/impl_<name>.md`.

## Cuándo NO aplica SDD

Features sin `"sdd": true` no tienen spec. SDD solo aplica hacia adelante.
