# Arquitectura — Qué significa "hacer un buen trabajo"

> Los revisores evalúan el código contra este archivo. Si no está aquí,
> no es un requisito.

## Stack

- **Lenguaje:** Python 3.10+
- **Framework:** FastAPI
- **ORM:** SQLAlchemy (Declarative Base)
- **Base de datos:** MySQL (producción) / SQLite en memoria (tests)
- **Validación/serialización:** Pydantic v2
- **Imágenes:** Cloudinary
- **PDFs:** WeasyPrint
- **Autenticación:** JWT via `app/core/security.py`

## Principios

1. **Capas claras.** Cuatro capas en orden estricto:
   - `controllers/` — Endpoints FastAPI (Routers). Solo entrada/salida HTTP.
   - `services/` — Lógica de negocio. Recibe repositories por inyección.
   - `repositories/` — Acceso a datos. Solo SQLAlchemy, sin lógica de dominio.
   - `models/` — Definición ORM (tablas). Sin métodos de negocio.
   - `schemas/` — DTOs Pydantic. Frontera entre capas y con el exterior.

2. **Interfaces antes que implementaciones.** Siempre crear:
   - `app/services/IXxxService.py` (ABC) antes de `app/services/imp/XxxService.py`.
   - `app/repositories/IXxxRepository.py` (ABC) antes de `app/repositories/imp/XxxRepository.py`.

3. **Inyección de dependencias.** Los servicios reciben repositories en
   `__init__`. Los controllers reciben servicios via `Depends()`.

4. **DTOs en el borde.** Los modelos ORM (`models/`) no salen de la capa
   de repositorio. Los controllers y responses usan siempre schemas Pydantic.

5. **Errores explícitos.** Usar `HTTPException` con código HTTP correcto.
   Los servicios pueden lanzar excepciones de dominio; el controller las
   convierte.

6. **Sin stock.** El sistema NO gestiona inventario. Nunca añadir lógica
   de decremento o disponibilidad en tiempo real.

## Flujo de datos

```
HTTP Request
    │
    ▼
Controller (Router FastAPI)
    │  valida entrada via Pydantic schema
    ▼
Service (IXxxService)
    │  lógica de negocio, sin SQL
    ▼
Repository (IXxxRepository)
    │  SQLAlchemy queries
    ▼
Model (SQLAlchemy ORM)
    │
    ▼
Base de datos (MySQL / SQLite)

HTTP Response ←── Pydantic schema (serialización)
```

## Estructura de módulos

```
app/
├── main.py               # FastAPI app, routers, middlewares
├── database.py           # Engine, SessionLocal, get_db
├── core/security.py      # JWT, obtener_usuario_confirmado, verificar_rol
├── controllers/          # Routers (un archivo por dominio)
├── services/
│   ├── IXxxService.py    # Interfaces ABC
│   └── imp/XxxService.py # Implementaciones
├── repositories/
│   ├── IXxxRepository.py
│   └── imp/XxxRepository.py
├── models/               # SQLAlchemy ORM models
└── schemas/              # Pydantic schemas (request + response)
```

## Qué NO hacer

- ❌ Lógica de negocio en controllers (ningún `if` de dominio en Routers).
- ❌ Consultas SQLAlchemy en services (solo en repositories).
- ❌ Modelos ORM como tipo de retorno de controllers.
- ❌ `print()` de debug en el código final.
- ❌ Endpoints públicos (sin auth) para operaciones de escritura.
- ❌ Gestión de stock (invariante de dominio: no existe en este sistema).
- ❌ Instanciar repositorios directamente en servicios sin inyección.
