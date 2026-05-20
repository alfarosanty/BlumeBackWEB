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
      `architecture.md` (controllers → services → repositories → models).
- [ ] No hay dependencias externas nuevas sin justificación en
      `requirements.txt` o `pyproject.toml`.
- [ ] Sin logs de debug sueltos (`print()` de debug), sin TODOs sin contexto.
- [ ] Toda lógica de negocio está en la capa `services`, no en controllers.
- [ ] Toda clase de servicio tiene su interface `IXxxService` definida.

## C4 — La verificación es real
- [ ] Al menos un test por endpoint nuevo (usando `TestClient` de FastAPI).
- [ ] Tests con fixtures reales (SQLite en memoria), no mocks de DB sin necesidad.
- [ ] `python -m pytest -q` muestra > 0 tests y todos verdes.

## C5 — La sesión se cerró bien
- [ ] Sin artefactos temporales sin trackear (`__pycache__/`, `*.pyc`
      cubiertos por `.gitignore`).
- [ ] `progress/history.md` tiene una entrada por la última sesión.
- [ ] La última feature está en su estado correcto.

## C6 — Spec Driven Development
- [ ] Toda feature `"sdd": true` en `spec_ready`/`in_progress`/`done`
      tiene `specs/<name>/` con los 3 archivos.
- [ ] `requirements.md` usa EARS estricto.
- [ ] Toda feature `done` con `"sdd": true` tiene todas sus tasks `[x]`.
- [ ] Cada `R<n>` cubierto por ≥1 test concreto en `tests/`.

---

**Uso:** el `reviewer` recorre cada checkbox, marca `[x]`/`[ ]`, y
rechaza el cierre si quedan boxes vacíos en C1–C6.
