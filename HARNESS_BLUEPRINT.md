# HARNESS BLUEPRINT — Sistema portable para cualquier proyecto

> **Qué es este archivo.** Un plano autosuficiente y **stack-agnóstico**
> del sistema *Harness Engineering + Spec Driven Development (SDD) +
> orquestación multi-agente + estado en disco*.
>
> **Para qué sirve.** Lo dejas en cualquier repo (con o sin
> documentación) y le pides a Claude: *"monta este arnés en este
> proyecto, detectando el stack y adaptando lo específico"*. Con este
> único archivo, Claude reconstruye todo el árbol y el comportamiento.
>
> **Diseñado para:** entorno **Windows** (PowerShell 5.1+), proyectos
> **Java Spring** (Maven o Gradle) y **React** (npm). El mecanismo es
> independiente del lenguaje; solo cambia el "perfil de stack" (§8).
>
> **Principio rector.** El *mecanismo* (roles, máquina de estados,
> puerta humana, anti-teléfono, trazabilidad) es **portable y se copia
> tal cual**. Los *comandos* (build/test) y las *reglas del proyecto*
> (arquitectura/convenciones/backlog) se **adaptan** por proyecto.

---

## 0. Instrucciones para la IA que reciba este archivo

Si eres una IA y te dan este archivo en un repo nuevo:

1. Lee este documento entero **una vez** antes de crear nada.
2. **Detecta el stack** mirando el repo:
   - `pom.xml` → Java Spring **Maven**.
   - `build.gradle` / `build.gradle.kts` → Java Spring **Gradle**.
   - `package.json` → **React** (mira `scripts.test`).
   - Si no hay señales, **pregunta** al humano.
   Elige el perfil correspondiente de la **§8**.
3. Pregunta (o deduce) **2 cosas**:
   - Las "capas"/módulos reales del proyecto → `docs/architecture.md`.
   - El backlog inicial de features → `feature_list.json`.
4. Crea los archivos de §5–§7 **en las rutas exactas**:
   - **[MECANISMO]** → copia casi literal (solo idioma/rutas).
   - **[CONTENIDO]** → **reescribe** desde cero para este proyecto.
   - **[PERFIL]** → rellena con los comandos de la §8 según el stack.
5. Ejecuta `.\init.ps1`. Debe terminar verde.
6. Recorre el checklist de la §11 y reporta qué creaste y qué adaptaste.

No saltes la §8 (perfiles) ni la §11 (checklist).

---

## 1. Los cuatro pilares

| Pilar | Idea | Manifestación física |
|-------|------|----------------------|
| **1. El repositorio ES el sistema** | El estado, las reglas y el plan viven en archivos versionados, no en el chat. Sobreviven a reinicios y context windows reventadas. | `AGENTS.md`, `init.ps1`, `feature_list.json`, `specs/`, `progress/`, `docs/` |
| **2. Orquestación multi-agente** | Roles que no se pisan: el que orquesta no codifica, el que especifica no codifica, el que implementa no se autoaprueba, el que revisa no edita. | `.claude/agents/{leader,spec_author,implementer,reviewer}.md` |
| **3. Spec Driven Development** | No se escribe código hasta que hay un spec aprobado por un humano. requirements (EARS) → design → tasks → code. | `docs/specs.md`, carpetas `specs/<feature>/` |
| **4. Supervisión enforced** | La verificación la ejecuta el harness (hooks), no el modelo: no se puede "saltar". | `.claude/settings.json`, `CHECKPOINTS.md`, `init.ps1` |

Conceptos transversales (preservar siempre, son independientes del stack):

- **Divulgación progresiva.** `AGENTS.md` es un *mapa*, no una biblia.
  El agente lee solo la sección que necesita, cuando la necesita.
- **Estado en disco, no en chat.** Specs, progreso e historial son
  archivos versionados.
- **Anti teléfono-descompuesto.** Los subagentes **escriben resultados
  en archivos** y devuelven una sola línea de referencia
  (`done -> progress/impl_x.md`). El orquestador nunca recibe el
  contenido por chat.
- **Trazabilidad obligatoria.** Cada requirement `R<n>` se mapea a ≥1
  test concreto. El reviewer rechaza si falta cobertura.
- **Una feature a la vez.** Validado por máquina (`init.ps1` rechaza más
  de un `in_progress`).
- **Puerta de aprobación humana.** El flujo se detiene UNA vez, en
  `spec_ready`: un humano lee el spec y aprueba antes de tocar código.

---

## 2. El árbol de archivos completo

```
.
├── CLAUDE.md                 # [MECANISMO] Auto-cargado. Fuerza el rol leader.
├── AGENTS.md                 # [MECANISMO] Mapa de navegación.
├── CHECKPOINTS.md            # [MECANISMO] Criterios de "estado final correcto".
├── feature_list.json         # [CONTENIDO] Backlog + máquina de estados.
├── init.ps1                  # [PERFIL]   Verificación ejecutable (PowerShell).
├── HARNESS_BLUEPRINT.md      # Este archivo (puedes dejarlo en el repo).
├── .claude/
│   ├── agents/
│   │   ├── leader.md         # [MECANISMO] Orquestador.
│   │   ├── spec_author.md    # [MECANISMO] Redacta specs.
│   │   ├── implementer.md    # [MECANISMO] Escribe código + tests.
│   │   └── reviewer.md       # [MECANISMO] Aprueba/rechaza.
│   └── settings.json         # [PERFIL]   Hooks (Windows/PowerShell).
├── docs/
│   ├── architecture.md       # [CONTENIDO] Qué es "buen trabajo" aquí.
│   ├── conventions.md        # [CONTENIDO] Estilo/nombres del lenguaje.
│   ├── specs.md              # [MECANISMO] Proceso SDD: EARS + puerta humana.
│   └── verification.md       # [CONTENIDO] Niveles de verificación del stack.
├── specs/
│   └── <feature-name>/       # Se crea por feature al dejar `pending`.
│       ├── requirements.md   #   EARS notation.
│       ├── design.md         #   Decisiones técnicas.
│       └── tasks.md          #   Checklist ejecutable.
├── progress/
│   ├── current.md            # [MECANISMO] Estado vivo (plantilla vacía).
│   ├── history.md            # [MECANISMO] Bitácora append-only.
│   ├── impl_<feature>.md     #   Lo escribe el implementer (no a mano).
│   └── review_<feature>.md   #   Lo escribe el reviewer (no a mano).
└── (código del proyecto)     # [PROYECTO] src/main, src/test, src/, etc.
```

Leyenda: **[MECANISMO]** copiar casi literal · **[CONTENIDO]**
reescribir para el proyecto · **[PERFIL]** rellenar con la §8 según el
stack · **[PROYECTO]** el código real, ajeno al arnés.

> **Rutas en Windows.** Usa `\` o `/` indistintamente; PowerShell acepta
> ambas. Los ejemplos usan `/` por compatibilidad y `.\init.ps1` para
> invocar el script.

---

## 3. El flujo SDD (la máquina de estados)

```
pending → [spec_author] → spec_ready → ⏸ HUMANO APRUEBA → in_progress → [implementer → reviewer] → done
                                                                                    │
                                                                              (CHANGES_REQUESTED)
                                                                                    ↓
                                                                            vuelve a implementer
```

| Estado | Significado | Quién actúa |
|--------|-------------|-------------|
| `pending` | Sin spec. | `spec_author` es el primero. |
| `spec_ready` | Spec drafted. **Esperando aprobación humana.** | nadie (pausa) |
| `in_progress` | Spec aprobado. | `implementer`, luego `reviewer`. |
| `done` | Verde, reviewer aprobó, sesión cerrada. | — |
| `blocked` | Atascado. Razón en `progress/current.md`. | humano resuelve |

Reglas duras: máximo **una** feature `in_progress` (lo valida
`init.ps1`); `spec_author` solo mueve `pending→spec_ready`; el leader
mueve `spec_ready→in_progress` **solo tras "aprobado"** humano; solo
leader/implementer (tras review APPROVED) marca `done`; features sin
`"sdd": true` no llevan spec.

---

## 4. Patrón Leader-Spec-Implementer-Reviewer

| Agente | Hace | NO hace | Salida (a chat) |
|--------|------|---------|-----------------|
| `leader` | Descompone, decide, lanza subagentes, gestiona estados, para en `spec_ready`. | Editar código. Marcar `done`. Saltar la puerta humana. | Referencias + mensaje al humano. |
| `spec_author` | Escribe `specs/<f>/{requirements,design,tasks}.md`. Marca `spec_ready`. | Tocar código/tests. Lanzar implementer. | `spec_ready -> specs/<f>/` |
| `implementer` | Ejecuta `tasks.md`, código + test por task, autoverifica, documenta trazabilidad. | Autoaprobarse. Marcar `done`. Inventar requisitos. | `done -> progress/impl_<f>.md` |
| `reviewer` | Verifica trazabilidad `R<n>↔test`, tasks, `docs/`, `CHECKPOINTS.md`, init verde. | Editar código. | `APPROVED -> progress/review_<f>.md` |

Escalado de esfuerzo (lo usa el leader): trivial → 1 spec_author → ⏸ → 1
implementer · media → +1 reviewer · compleja → +2-3 exploradores antes
del spec_author · muy compleja → divide y reaplica.

---

## 5. Archivos [MECANISMO] — copiar casi literal

> Solo cambia idioma (si trabajas en inglés) y rutas si difieren. Roles y
> reglas se preservan. **Son independientes del lenguaje del proyecto.**

### 5.1 `CLAUDE.md` (raíz)

````markdown
# Instrucciones para Claude

> Este archivo se carga automáticamente al inicio de cada sesión.

## Rol obligatorio: leader

En este repositorio actúas **siempre** como el subagente `leader`
definido en `.claude/agents/leader.md`. Tu trabajo es **descomponer y
coordinar**, nunca implementar.

### Reglas duras

- ❌ No edites el código de la aplicación ni los tests directamente.
- ❌ No marques features como `done` en `feature_list.json`.
- ❌ No saltes la fase de spec. Toda feature con `"sdd": true` pasa por
  `spec_author` antes de implementar.
- ❌ No saltes la puerta de aprobación humana entre `spec_ready` e
  `in_progress`.
- ✅ Para tareas de código lanza el subagente vía `Agent`:
  `spec_author` → `implementer` → `reviewer`. Investigación previa:
  2-3 exploradores en paralelo.

### Protocolo de arranque

1. Lee `AGENTS.md`.
2. Lee `feature_list.json` y `progress/current.md`.
3. Ejecuta `.\init.ps1`. Si falla, paras y reportas.
4. Aplica la tabla de escalado y el flujo SDD de
   `.claude/agents/leader.md`.

### Regla anti-teléfono-descompuesto

Instruye a los subagentes para escribir resultados en archivos y
devolverte solo la referencia, no el contenido.

### Cuándo NO aplica este rol

- Preguntas conceptuales o de exploración (lectura pura) → responde tú.
- Cambios fuera del código y los tests (docs, config, `progress/`) →
  puedes editar tú mismo.
````

### 5.2 `AGENTS.md`

````markdown
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
| `docs/architecture.md` | Qué es "buen trabajo" | Antes de implementar |
| `docs/conventions.md` | Estilo, nombres, errores | Antes de escribir código |
| `docs/specs.md` | Proceso SDD | Antes de redactar/leer un spec |
| `docs/verification.md` | Cómo verificar | Antes de declarar `done` |
| `CHECKPOINTS.md` | Estado final correcto | Para auto-evaluarte |
| `.claude/agents/` | Definiciones de subagentes | Si orquestas trabajo |

## 3. Reglas duras (no negociables)

- Una sola feature a la vez.
- No declares `done` sin verificación verde (`.\init.ps1` al 100%).
- No saltes la fase de spec ni la aprobación humana.
- Documenta en `progress/current.md` **mientras** trabajas, no al final.
- Deja el repo limpio antes de cerrar.
- Si no sabes algo, búscalo en `docs/` antes de inventarlo.

## 4. Flujo SDD

pending → [spec_author] → spec_ready → ⏸ HUMANO → in_progress →
[implementer → reviewer] → done

## 5. Cierre de sesión

1. `.\init.ps1` verde.
2. Si la tarea acabó: `status: "done"` en `feature_list.json`.
3. Mueve el resumen de `progress/current.md` al final de `history.md`.
4. Vacía `progress/current.md` dejando la plantilla.
5. Sin temporales, sin logs de debug, sin TODOs sin contexto.

## 6. Si te bloqueas

Relee `docs/`. No inventes workarounds: documenta el bloqueo en
`progress/current.md` con estado `blocked` y para.
````

### 5.3 `.claude/agents/leader.md`

````markdown
---
name: leader
description: Orquestador. Recibe la tarea principal, divide el trabajo y lanza subagentes. NUNCA escribe código directamente.
tools: Read, Glob, Grep, Bash, Agent
---

# Agente Líder (Orquestador)

Tu único trabajo es **descomponer y coordinar**, nunca implementar.

## Protocolo de arranque

1. Lee `AGENTS.md`.
2. Lee `feature_list.json` y `progress/current.md`.
3. Ejecuta `.\init.ps1`. Si falla, paras y reportas.

## Flujo SDD (obligatorio)

pending → [spec_author] → spec_ready → ⏸ HUMANO APRUEBA → in_progress →
[implementer → reviewer] → done

NUNCA saltes la fase de spec. NUNCA lances implementer si está `pending`.

## Cómo descomponer «implementa la siguiente feature pendiente»

Mira el status de la primera feature no-`done`/no-`blocked`:

### Caso A — status == `pending`
1. Lanza 1 `spec_author`.
2. Redacta `specs/<name>/{requirements,design,tasks}.md` → `spec_ready`.
3. **PARAS.** Mensaje al humano: "Spec listo en `specs/<name>/`. Di
   'aprobado' para continuar, o pide cambios."

### Caso B — `spec_ready` Y el humano acaba de aprobar
1. Cambia status a `in_progress`.
2. Lanza 1 `implementer` con la ruta `specs/<name>/` como input.
3. Al terminar → 1 `reviewer`.

### Caso C — `spec_ready` SIN aprobación humana
NO continúes. Recuérdale al humano qué le toca.

### Caso D — `in_progress`
Sesión interrumpida. Pregunta si reanudas o abortas.

## Regla anti-teléfono-descompuesto

Los subagentes **escriben resultados en archivos**. Tú solo recibes
referencias: `done -> progress/impl_<name>.md`,
`spec_ready -> specs/<name>/`.

## Escalado de esfuerzo

| Complejidad | Subagentes |
|---|---|
| Trivial | 1 spec_author → ⏸ → 1 implementer |
| Media | 1 spec_author → ⏸ → 1 implementer → 1 reviewer |
| Compleja | 2-3 exploradores → 1 spec_author → ⏸ → 1 implementer → 1 reviewer |
| Muy compleja | Divide y reaplica la tabla |

## Qué NO haces

- ❌ Editar el código de la aplicación o los tests.
- ❌ Marcar features como `done`.
- ❌ Saltar la puerta de aprobación humana.
- ❌ Aceptar resultados de subagentes sin referencia a archivo.
````

### 5.4 `.claude/agents/spec_author.md`

````markdown
---
name: spec_author
description: Redacta specs Kiro-style (requirements/design/tasks) para una feature pending con "sdd": true. NUNCA escribe código de aplicación ni tests.
tools: Read, Write, Edit, Glob, Grep, Bash
---

# Agente Spec Author

Produces tres archivos para **exactamente una** feature `pending` con
`"sdd": true`:
- `specs/<name>/requirements.md`
- `specs/<name>/design.md`
- `specs/<name>/tasks.md`

No escribes código ni tests.

## Protocolo

1. Lee `AGENTS.md`, `docs/architecture.md`, `docs/conventions.md`,
   `docs/specs.md`.
2. Toma la feature `pending` de menor `id` con `"sdd": true`. Crea
   `specs/<name>/`.
3. `requirements.md` en **EARS estricto** (ver `docs/specs.md`). Cada
   criterio del `acceptance` original cubierto por ≥1 `R<n>`.
4. `design.md`: archivos a tocar, firmas/clases nuevas, excepciones,
   alternativa descartada con justificación.
5. `tasks.md`: pasos discretos en orden, cada uno con `[ ]` y los `R<n>`
   que cubre.
6. Cambia el `status` a `spec_ready`.
7. **PARA.** No invoques al implementer. Espera la aprobación humana.

## Reglas duras

- ❌ NUNCA edites código ni tests.
- ❌ NUNCA marques `in_progress` o `done`. Solo `spec_ready`.
- ✅ Si el `acceptance` es insuficiente, paras con `blocked` y pides
  clarificación. No inventes requisitos.
- ✅ Cada `R<n>` DEBE ser verificable por un test concreto.

## Comunicación

Salida final: **una sola línea**.
`spec_ready -> specs/<name>/`  o  `blocked -> progress/spec_<name>.md`
Nunca devuelvas el contenido del spec en chat — vive en disco.
````

### 5.5 `.claude/agents/implementer.md`

````markdown
---
name: implementer
description: Trabajador. Implementa UNA feature según su spec aprobado. Escribe código, escribe tests y se autoverifica.
tools: Read, Write, Edit, Glob, Grep, Bash
---

# Agente Implementador

Ejecutas **una sola** feature siguiendo su spec aprobado en
`specs/<name>/`.

## Pre-condiciones

- La feature está `in_progress`. Si está `pending`/`spec_ready`, paras.
- Existen los 3 archivos en `specs/<name>/`. Si falta alguno, paras.

## Protocolo

1. Lee `AGENTS.md`, `docs/architecture.md`, `docs/conventions.md`,
   `docs/specs.md`.
2. Lee el spec completo. Cada `T<n>` es lo que harás; cada `R<n>` es lo
   que debe quedar verdadero.
3. Anota en `progress/current.md`: feature en curso + plan (T1..Tn).
4. Por cada task `T<n>` en orden: implementa, escribe su test, marca
   `[x] T<n>` en `tasks.md`.
5. Verifica ejecutando `.\init.ps1`. Si falla → vuelve a 4.
6. Trazabilidad: cada `R<n>` cubierto por ≥1 test concreto. Documenta el
   mapa `R<n> → test` en `progress/impl_<name>.md`.
7. **No marques `done` tú mismo.** Espera al reviewer.
8. Si el reviewer aprueba (te lo dirá el leader): cambias a `done` y
   mueves el resumen a `progress/history.md`.

## Reglas duras

- ❌ Si no está `in_progress` con spec aprobado, paras.
- ❌ Una sola feature por sesión.
- ❌ Si no puedes completar una task sin desviarte del spec, paras y
  reportas. Pide cambios al spec primero.
- ✅ Todo código va con su test antes de la siguiente task.
- ✅ Si una herramienta falla raro, NO improvises. Para, anota `blocked`.

## Comunicación

Salida final: **una sola línea**.
`done -> progress/impl_<name>.md`  o  `blocked -> progress/impl_<name>.md`
Nunca devuelvas el diff completo en chat.
````

### 5.6 `.claude/agents/reviewer.md`

````markdown
---
name: reviewer
description: Revisor automático. Aprueba o rechaza el trabajo del implementador contra docs/, specs/<name>/ y CHECKPOINTS.md.
tools: Read, Glob, Grep, Bash
---

# Agente Revisor

Tu única función es **aprobar o rechazar**. No editas código.

## Protocolo

1. Lee `docs/architecture.md`, `docs/conventions.md`, `docs/specs.md`,
   `CHECKPOINTS.md`.
2. Identifica la feature `in_progress` y abre `specs/<name>/`.
3. **Trazabilidad**: por cada `R<n>`, localiza ≥1 test concreto que lo
   verifique. Si falta cobertura, rechaza.
4. **Tasks**: TODAS las tasks de `tasks.md` en `[x]`. Si queda `[ ]` sin
   justificación documentada, rechaza.
5. Por cada archivo modificado: ¿respeta `architecture.md`?
   ¿`conventions.md`? ¿tiene test?
6. Ejecuta `.\init.ps1`. Verde obligatorio.
7. Recorre `CHECKPOINTS.md`: marca `[x]`/`[ ]`.
8. Emite veredicto.

## Formato del veredicto

Escribe un único bloque en `progress/review_<name>.md` con: Veredicto
(APPROVED|CHANGES_REQUESTED), trazabilidad `R<n>↔test`, tasks completas,
checkpoints, y cambios requeridos si aplica.

Respuesta en chat: **una sola línea**.
`APPROVED -> progress/review_<name>.md`  o
`CHANGES_REQUESTED -> progress/review_<name>.md`

## Reglas duras

- ❌ Nunca apruebes con tests rojos.
- ❌ Nunca apruebes con `.\init.ps1` en rojo.
- ❌ Nunca apruebes si algún `R<n>` queda sin test.
- ❌ Nunca apruebes si quedan tasks `[ ]` sin justificación.
- ❌ Nunca edites el código. Di qué falla, no lo arregles.
- ✅ Sé concreto: cita líneas y archivos.
````

### 5.7 `docs/specs.md` — proceso SDD (núcleo conceptual)

````markdown
# Spec Driven Development (SDD)

> Flujo Kiro-style: requirements → design → tasks → code. El código no se
> escribe hasta que el spec está aprobado por un humano.

## Estructura

Cada feature `"sdd": true` tiene `specs/<feature-name>/` con:
`requirements.md` (QUÉ, EARS), `design.md` (CÓMO), `tasks.md` (PASOS).
`<feature-name>` = campo `name` de `feature_list.json`.

## Estados

pending → [spec_author] → spec_ready → ⏸ HUMANO → in_progress →
[implementer → reviewer] → done

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

(En inglés: SHALL / WHEN...SHALL / WHILE...SHALL / WHERE...SHALL /
IF...THEN...SHALL.)

Reglas: id estable; cada `R<n>` verificable por ≥1 test; no mezclar
varios `DEBE`; solo `DEBE`/`NO DEBE` (nada de "podría", "soporta").

## design.md — decisiones técnicas

Antes de tocar código: archivos a crear/modificar, firmas/clases nuevas,
excepciones, y **mínimo una alternativa descartada con su porqué**.
Apóyate en `architecture.md`/`conventions.md`; documenta solo dónde la
feature roza la frontera de esas reglas.

## tasks.md — checklist ejecutable

Pasos discretos en orden, cada uno con checkbox y los `R<n>` que cubre.
Ejemplo:
- [ ] T1 — Añadir X. Cubre: R1, R3.
- [ ] T2 — Test de Y. Cubre: R2.

El implementer marca `[x]`. El reviewer rechaza si queda `[ ]` sin
justificación.

## Trazabilidad (regla dura)

Cada test mapea a un `R<n>`; cada `R<n>` tiene ≥1 test. El reviewer lo
comprueba. El implementer documenta el mapa en `progress/impl_<name>.md`.

## Cuándo NO aplica SDD

Features sin `"sdd": true` no tienen spec. SDD solo aplica hacia adelante.
````

### 5.8 `CHECKPOINTS.md` (genérico, stack-agnóstico)

````markdown
# CHECKPOINTS — Evaluación del estado final

> No se evalúa el camino, se evalúa el destino. Un juez (humano o IA)
> usa estos checkpoints para decidir si el proyecto está sano.

## C1 — El arnés está completo
- [ ] Existen los archivos base: `AGENTS.md`, `init.ps1`,
      `feature_list.json`, `progress/current.md`.
- [ ] Existen los docs: `architecture.md`, `conventions.md`,
      `verification.md`, `specs.md`.
- [ ] `.\init.ps1` termina con exit code 0.

## C2 — El estado es coherente
- [ ] Como mucho una feature en `in_progress`.
- [ ] Toda feature `done` tiene tests que pasan.
- [ ] `progress/current.md` vacío o describe la sesión activa.

## C3 — El código respeta la arquitectura
- [ ] El código solo contiene los módulos/capas previstos en
      `architecture.md`.
- [ ] No hay dependencias externas no justificadas en el manifiesto de
      build (`pom.xml` / `build.gradle` / `package.json`).
- [ ] Sin logs de debug sueltos, sin TODOs sin contexto.

## C4 — La verificación es real
- [ ] Al menos un test por módulo/componente con lógica.
- [ ] Tests con fixtures reales, no mocks de I/O crítico sin necesidad.
- [ ] El runner muestra > 0 tests y todos verdes.

## C5 — La sesión se cerró bien
- [ ] Sin artefactos temporales sospechosos sin trackear
      (`target/`, `build/`, `node_modules/`, `dist/` deben estar en
      `.gitignore`).
- [ ] `progress/history.md` tiene una entrada por la última sesión.
- [ ] La última feature está en su estado correcto.

## C6 — Spec Driven Development
- [ ] Toda feature `"sdd": true` en `spec_ready`/`in_progress`/`done`
      tiene `specs/<name>/` con los 3 archivos.
- [ ] `requirements.md` usa EARS estricto.
- [ ] Toda feature `done` con `"sdd": true` tiene todas sus tasks `[x]`.
- [ ] Cada `R<n>` cubierto por ≥1 test concreto.

---

**Uso:** el `reviewer` recorre cada checkbox, marca `[x]`/`[ ]`, y
rechaza el cierre si quedan boxes vacíos en C1–C6.
````

### 5.9 Plantillas de `progress/`

`progress/current.md` (estado inicial; se vacía a esto al cerrar sesión):

````markdown
# Sesión actual

> Este archivo se vacía al cerrar cada sesión y se mueve a `history.md`.
> Mientras trabajas, **mantenlo actualizado en tiempo real**, no al final.

- **Feature en curso:** _ninguna_
- **Inicio:** _—_
- **Agente:** _—_

## Plan

_—_

## Bitácora

_—_

## Próximo paso

_—_
````

`progress/history.md` (solo la cabecera; crece append-only):

````markdown
# Bitácora histórica (append-only)

> Cada vez que se cierra una sesión, su resumen se añade aquí.
> No edites entradas anteriores. Solo añades al final.

---
````

Formato de cada entrada al cerrar:

````markdown
## YYYY-MM-DD — Feature <id>: <name>
- **Agente:** <quién> (leader → spec_author → implementer → reviewer)
- **Plan:** <una línea>
- **Cambios:** <archivos tocados>
- **Verificación:** init verde, N tests pasan. Reviewer APPROVED.
- **Cierre:** feature <id> marcada `done`. Próximo: feature <id+1>.
````

---

## 6. Archivos [CONTENIDO] — reescribir para el proyecto

**NO copies ejemplos de otro proyecto.** Estos archivos definen las
reglas del proyecto concreto.

### 6.1 `docs/architecture.md` — esqueleto

````markdown
# Arquitectura — Qué significa "hacer un buen trabajo"

> Los revisores evalúan el código contra este archivo. Si no está aquí,
> no es un requisito.

## Principios
1. **Capas claras.** <enumera las capas reales y su responsabilidad. No
   introducir capas extra sin justificación documentada.>
2. **Dependencias.** <política de dependencias del proyecto.>
3. **Errores explícitos.** <cómo se señalan fallos en este stack.>
4. **<invariantes del dominio>**.

## Flujo de datos
<diagrama ASCII del flujo principal>

## Qué NO hacer
<anti-patrones concretos de este proyecto>
````

**Java Spring** (rellenar): capas `controller → service →
repository → entity/dto`; inyección por constructor (no `@Autowired` en
campos); excepciones de dominio + `@ControllerAdvice`; nada de lógica de
negocio en controllers; DTOs en el borde, entidades no salen de la capa
de servicio.

**React** (rellenar): capas `components → hooks → services/api →
state`; componentes presentacionales sin fetch directo; lógica en
hooks/servicios; estado del servidor vs estado de UI separados; sin
lógica de negocio en JSX.

### 6.2 `docs/conventions.md`

Estilo, nombres y manejo de errores del lenguaje del proyecto. Cubre:
runtime/versión, formatter/linter, naming, estructura de archivo,
convención de tests, jerarquía de errores, política de comentarios.

- **Java Spring:** Java 17/21, Google Java Format o Spotless, Checkstyle;
  paquetes por feature; tests JUnit 5 + `@SpringBootTest`/`@WebMvcTest`;
  AssertJ; excepciones que extienden `RuntimeException` del dominio.
- **React:** TypeScript estricto, ESLint + Prettier; componentes
  `PascalCase`, hooks `useCamelCase`; tests con Vitest/Jest +
  Testing Library; sin `any`; errores vía error boundaries / `Result`.

### 6.3 `feature_list.json` — estructura exacta

````json
{
  "project": "<nombre>",
  "description": "<una línea>",
  "rules": {
    "one_feature_at_a_time": true,
    "require_tests_to_close": true,
    "require_approved_spec_to_implement": true,
    "valid_status": ["pending", "spec_ready", "in_progress", "done", "blocked"],
    "sdd_required_when": "feature has \"sdd\": true"
  },
  "features": [
    {
      "id": 1,
      "name": "<slug_sin_espacios>",
      "title": "<título legible>",
      "description": "<qué hace>",
      "acceptance": [
        "<criterio verificable 1>",
        "<criterio verificable 2>",
        "<criterio que exige tests concretos>"
      ],
      "sdd": true,
      "status": "pending"
    }
  ]
}
````

`name` = nombre de carpeta en `specs/<name>/`. Los `acceptance` deben ser
verificables. Deja ≥1 feature `"status": "pending"` con `"sdd": true`.

### 6.4 `docs/verification.md`

Niveles de verificación (adaptar comandos al stack): **N1** tests
unitarios (camino feliz + ≥1 error); **N2** integración (ejecutar la
unidad real contra fixture, no mock de I/O crítico); **N3** smoke
end-to-end opcional; **N4** trazabilidad `R<n>↔test` (obligatorio para
`"sdd": true`). Regla de oro: *"el agente no dice que funciona, lo
demuestra"*. Comando concreto según §8.

---

## 7. Archivos [PERFIL] — Windows / PowerShell

### 7.1 `init.ps1` (raíz) — verificación ejecutable

> PowerShell 5.1 compatible. Validación de `feature_list.json` en
> **PowerShell puro** (cero dependencia de Python). Editas **una sola
> línea**: `$TestCommand` (ver §8).

````powershell
#requires -Version 5.1
$ErrorActionPreference = 'Stop'
$exit = 0

function Ok($m)   { Write-Host "[OK]    $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[WARN]  $m" -ForegroundColor Yellow }
function Fail($m) { Write-Host "[FAIL]  $m" -ForegroundColor Red }

# >>> EDITA SOLO ESTA LINEA segun el perfil de stack (ver blueprint §8) <<<
$TestCommand = 'mvn -q -B test'
# Java Gradle : '.\gradlew.bat test'
# React (npm) : 'npm test --silent -- --run'   (vitest) o 'npm test -- --watchAll=false' (jest/CRA)

Write-Host "-- 1. Archivos base del arnes --------------------------"
$base = @('AGENTS.md','feature_list.json','progress/current.md',
          'docs/architecture.md','docs/conventions.md',
          'docs/verification.md','CHECKPOINTS.md')
foreach ($f in $base) {
  if (Test-Path $f) { Ok "Existe $f" } else { Fail "Falta $f"; $exit = 1 }
}

Write-Host ""
Write-Host "-- 2. Validando feature_list.json y specs --------------"
try {
  $data  = Get-Content 'feature_list.json' -Raw -Encoding UTF8 | ConvertFrom-Json
  $valid = @('pending','spec_ready','in_progress','done','blocked')
  $need  = @('spec_ready','in_progress','done')
  $inProgress = @($data.features | Where-Object { $_.status -eq 'in_progress' })
  if ($inProgress.Count -gt 1) {
    Fail "Hay $($inProgress.Count) features in_progress (maximo 1)"; $exit = 1
  }
  $specErrors = @()
  foreach ($f in $data.features) {
    if ($valid -notcontains $f.status) {
      Fail "Estado invalido en feature $($f.id): $($f.status)"; $exit = 1
    }
    $isSdd = $false
    if ($f.PSObject.Properties.Name -contains 'sdd') { $isSdd = [bool]$f.sdd }
    if ($isSdd -and ($need -contains $f.status)) {
      $dir = Join-Path 'specs' $f.name
      foreach ($n in @('requirements.md','design.md','tasks.md')) {
        if (-not (Test-Path (Join-Path $dir $n))) {
          $specErrors += "feature $($f.id) ($($f.name)) en $($f.status) sin $dir/$n"
        }
      }
    }
  }
  if ($specErrors.Count -gt 0) {
    foreach ($e in $specErrors) { Fail $e }
    $exit = 1
  } else {
    Ok "feature_list.json valido ($($data.features.Count) features)"
    Ok "Specs presentes para features sdd no-pending"
  }
} catch {
  Fail "feature_list.json o specs invalidos: $($_.Exception.Message)"
  $exit = 1
}

Write-Host ""
Write-Host "-- 3. Ejecutando tests ---------------------------------"
Write-Host "    > $TestCommand"
cmd /c $TestCommand
if ($LASTEXITCODE -ne 0) { Fail "Tests rojos (exit $LASTEXITCODE)"; $exit = 1 }
else { Ok "Tests verdes" }

Write-Host ""
Write-Host "-- 4. Resumen ------------------------------------------"
if ($exit -eq 0) { Ok "Entorno listo. Puedes trabajar." }
else { Fail "Entorno NO listo. Resuelve los errores antes de avanzar." }
exit $exit
````

> El validador de `feature_list.json` de arriba está **probado en
> PowerShell 5.1**. La única línea específica del proyecto es
> `$TestCommand`.

### 7.2 `.claude/settings.json` — hooks (Windows/PowerShell)

````json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File init.ps1",
            "description": "Tras editar/escribir, corre la verificación completa."
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File init.ps1",
            "description": "Antes de cerrar la sesión, fuerza la verificación."
          }
        ]
      }
    ]
  },
  "permissions": {
    "allow": [
      "Bash(powershell -NoProfile -ExecutionPolicy Bypass -File init.ps1)",
      "PowerShell(.\\init.ps1)"
    ]
  }
}
````

> **Stacks lentos (Java).** `mvn test` en cada `Edit|Write` es costoso.
> Opciones: (a) deja **solo** el hook `Stop`; (b) en `PostToolUse` usa un
> subconjunto rápido (`mvn -q -B -Dtest=...Fast test` o
> `npm test -- --changed`); (c) mantén ambos y asume el coste. El hook
> `Stop` (verificación completa antes de cerrar) es el irrenunciable.

### 7.3 `.gitignore` (añadir, según stack)

```
# Java
target/
build/
.gradle/
# React
node_modules/
dist/
coverage/
# Harness temp
*.tmp
```

---

## 8. Perfiles de stack (rellenar `[PERFIL]` con esto)

| | **Java Spring (Maven)** | **Java Spring (Gradle)** | **React (npm)** |
|---|---|---|---|
| Detección | `pom.xml` | `build.gradle(.kts)` | `package.json` |
| `$TestCommand` en `init.ps1` | `mvn -q -B test` | `.\gradlew.bat test` | vitest: `npm test --silent -- --run` · jest/CRA: `npm test -- --watchAll=false` |
| Build/compilar | `mvn -q -B compile` | `.\gradlew.bat build -x test` | `npm run build` |
| Carpeta de tests | `src/test/java` | `src/test/java` | `src/**/*.test.tsx` o `__tests__/` |
| Framework de test | JUnit 5 + AssertJ | JUnit 5 + AssertJ | Vitest/Jest + Testing Library |
| Capas (architecture.md) | controller→service→repository→entity | idem | components→hooks→services→state |
| Convención (conventions.md) | Java 17/21, Spotless, Checkstyle | idem | TS estricto, ESLint, Prettier |
| `permissions.allow` extra | `Bash(mvn *)` | `Bash(*gradlew*)` | `Bash(npm *)`, `Bash(npx *)` |
| `.gitignore` clave | `target/` | `build/ .gradle/` | `node_modules/ dist/ coverage/` |

Para añadir otro stack: replica la columna definiendo `$TestCommand`,
las capas y la convención. **Nada más del mecanismo cambia.**

---

## 9. Cómo se usa, una vez montado (operación)

1. `.\init.ps1` — debe terminar verde.
2. En `feature_list.json`, asegura ≥1 feature `"status": "pending"` con
   `"sdd": true`.
3. Abre Claude en la raíz del repo. `CLAUDE.md` lo fuerza a actuar como
   `leader`.
4. Pídele: **«implementa la siguiente feature pendiente»**.

- **Fase 1 — Spec.** El leader lanza `spec_author`, que escribe
  `specs/<feature>/{requirements,design,tasks}.md`, deja la feature en
  `spec_ready` y **para pidiendo aprobación**. Lees los 3 archivos y
  dices "aprobado" (o pides cambios).
- **Fase 2 — Código.** El leader pasa a `in_progress`, lanza
  `implementer` (tasks una a una, marcando `[x]`) y luego `reviewer`. Al
  aprobar, se marca `done` y el resumen va a `progress/history.md`.

Dónde queda la traza (abre `specs/` y `progress/` en tu editor mientras
trabaja):

| Archivo | Quién lo escribe | Qué contiene |
|---|---|---|
| `specs/<f>/requirements.md` | spec_author | EARS `R1`, `R2`, ... |
| `specs/<f>/design.md` | spec_author | Decisiones + alternativa descartada |
| `specs/<f>/tasks.md` | spec_author | Checklist; implementer marca `[x]` |
| `progress/current.md` | leader/implementer | Plan vivo de la sesión |
| `progress/impl_<f>.md` | implementer | Archivos tocados + mapa `R<n>→test` |
| `progress/review_<f>.md` | reviewer | Checklist contra docs/CHECKPOINTS |
| `feature_list.json` | leader/implementer | Máquina de estados |
| `progress/history.md` | leader | Resumen append-only al cerrar |

---

## 10. Tabla maestra: qué copiar vs qué reescribir

| Archivo | Clase | Acción al replicar |
|---|---|---|
| `CLAUDE.md` | MECANISMO | Copiar; ajustar rutas. |
| `AGENTS.md` | MECANISMO | Copiar; ajustar el mapa si añades docs. |
| `.claude/agents/leader.md` | MECANISMO | Copiar tal cual. |
| `.claude/agents/spec_author.md` | MECANISMO | Copiar tal cual. |
| `.claude/agents/implementer.md` | MECANISMO | Copiar tal cual. |
| `.claude/agents/reviewer.md` | MECANISMO | Copiar tal cual. |
| `docs/specs.md` | MECANISMO | Copiar; traducir EARS si trabajas en inglés. |
| `CHECKPOINTS.md` | MECANISMO | Copiar (ya es genérico). |
| `progress/current.md` | MECANISMO | Copiar la plantilla vacía. |
| `progress/history.md` | MECANISMO | Copiar solo la cabecera. |
| `init.ps1` | PERFIL | Copiar; editar **solo** `$TestCommand` (§8). |
| `.claude/settings.json` | PERFIL | Copiar; ajustar `permissions` (§8). |
| `.gitignore` | PERFIL | Copiar el bloque del stack (§8). |
| `docs/architecture.md` | CONTENIDO | **Reescribir** para el proyecto. |
| `docs/conventions.md` | CONTENIDO | **Reescribir** para el lenguaje. |
| `docs/verification.md` | CONTENIDO | **Reescribir** comandos del stack. |
| `feature_list.json` | CONTENIDO | **Reescribir** con el backlog real. |
| `specs/*`, `progress/impl_*`, `progress/review_*` | GENERADO | No crear a mano; los generan los agentes. |
| código y tests del proyecto | PROYECTO | Ajeno al arnés. |

---

## 11. Checklist final (la IA lo verifica antes de reportar)

- [ ] Los 6 archivos MECANISMO existen y conservan roles/reglas.
- [ ] `CLAUDE.md` está en la raíz (se auto-carga → fuerza rol leader).
- [ ] Los 4 `.claude/agents/*.md` tienen frontmatter válido
      (`name`, `description`, `tools`).
- [ ] `docs/architecture.md` y `docs/conventions.md` describen ESTE
      proyecto y su stack (no un ejemplo ajeno).
- [ ] `feature_list.json` tiene backlog real, estados válidos, y ≥1
      feature `pending` con `"sdd": true`.
- [ ] `init.ps1` existe, tiene `$TestCommand` ajustado al perfil (§8), y
      `.\init.ps1` termina verde.
- [ ] `.claude/settings.json` apunta a `init.ps1` y `permissions`
      incluye los comandos del stack.
- [ ] `.gitignore` ignora artefactos de build del stack.
- [ ] `progress/current.md` en estado plantilla; `history.md` solo
      cabecera.
- [ ] Ninguna regla del mecanismo se perdió: una feature a la vez,
      puerta humana en `spec_ready`, anti-teléfono (resultados a disco +
      referencia de una línea), trazabilidad `R<n>↔test`, reviewer no
      edita código.

Si todo está marcado, el arnés está replicado y operativo.

---

## Apéndice — Variante POSIX/bash (si algún repo no es Windows)

Si un repo destino corre en Linux/macOS, sustituye `init.ps1` por
`init.sh` (mismo flujo: archivos base → validar `feature_list.json` →
tests → resumen → `exit $code`) y en `.claude/settings.json` cambia el
`command` de los hooks a `./init.sh ...`. El validador de
`feature_list.json` puede ir en cualquier lenguaje disponible (jq,
python, node); el resto del mecanismo es idéntico. No mezcles: un repo
usa `init.ps1` **o** `init.sh`, no ambos.
