# AGENTS.md — Mapa de navegación para agentes de IA

> Punto de entrada. NO es una biblia: es un MAPA. Lee solo lo que
> necesites cuando lo necesites.

## 1. Antes de empezar (obligatorio)

1. Ejecuta `.\init.ps1`. Si falla, **para**.
2. Lee `progress/current.md` (estado de la última sesión).
3. Lee `feature_list.json`. Feature `"sdd": true` → SDD (`docs/specs.md`).
4. Lee `docs/specs.md` antes de tocar cualquier spec.

## 2. Mapa del repositorio

| Archivo / carpeta | Qué contiene | Cuándo leerlo |
|---|---|---|
| `feature_list.json` | Backlog + estado | Siempre, al empezar |
| `progress/current.md` | Sesión actual | Siempre, al empezar |
| `progress/history.md` | Bitácora append-only | Si necesitas histórico |
| `specs/<feature>/` | requirements + design + tasks | Antes de implementar feature sdd |
| `docs/architecture.md` | Qué es "buen trabajo" aquí | Antes de implementar |
| `docs/conventions.md` | Estilo, nombres, errores | Antes de escribir código |
| `docs/specs.md` | Proceso SDD | Antes de redactar/leer un spec |
| `docs/verification.md` | Cómo verificar con pytest | Antes de declarar `done` |
| `CHECKPOINTS.md` | Estado final correcto | Para auto-evaluarte |
| `.claude/agents/` | Definiciones de subagentes | Si orquestas trabajo |
| `spec.md` | Contexto técnico del proyecto | Siempre, referencia |

## 3. Reglas duras (no negociables)

- Una sola feature a la vez.
- No declares `done` sin verificación verde (`.\init.ps1` al 100%).
- No saltes la fase de spec ni la aprobación humana.
- Documenta en `progress/current.md` **mientras** trabajas, no al final.
- Deja el repo limpio antes de cerrar.
- Si no sabes algo, búscalo en `docs/` antes de inventarlo.

## 4. Flujo SDD

```
pending → [spec_author] → spec_ready → ⏸ HUMANO → in_progress →
[implementer → reviewer] → done
```

## 5. Cierre de sesión

1. `.\init.ps1` verde.
2. Si la tarea acabó: `status: "done"` en `feature_list.json`.
3. Mueve el resumen de `progress/current.md` al final de `history.md`.
4. Vacía `progress/current.md` dejando la plantilla.
5. Sin temporales, sin logs de debug, sin TODOs sin contexto.

## 6. Si te bloqueas

Relee `docs/`. No inventes workarounds: documenta el bloqueo en
`progress/current.md` con estado `blocked` y para.
