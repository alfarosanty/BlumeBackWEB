# Design — get_articulos_maestro

## Archivos a crear

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `app/schemas/ApiResponseSchema.py` | CREAR | Wrappers genéricos `ApiResponse[T]` y `PagedResult[T]` |
| `app/schemas/ArticuloMaestroSchema.py` | CREAR | DTOs: `MedidaDto`, `SectorDto`, `FamiliaConSectorDto`, `SubFamiliaConJerarquiaDto`, `ArticuloPrecioConMedidaDto`, `ArticuloMaestroDto` |
| `app/repositories/IArticuloMaestroRepository.py` | CREAR | Interface ABC con `obtener_paginado()` |
| `app/repositories/imp/ArticuloMaestroRepository.py` | CREAR | Implementación de la query compleja |
| `app/services/IArticuloMaestroService.py` | MODIFICAR | Agregar `obtener_paginado()` al ABC |
| `app/services/imp/ArticuloMaestroService.py` | CREAR | Implementación del servicio |
| `app/controllers/ArticuloController.py` | MODIFICAR | Reemplazar `GET /articulos/maestro` roto con la nueva implementación y DTO |
| `app/models/ArticuloMaestroXArticuloPrecio.py` | MODIFICAR | Agregar relationships `subfamilia` y `articulo_precio` para poder hacer joinedload |

> **Sin controller nuevo.** El endpoint `GET /articulos/maestro` vive en `ArticuloController.py` existente. Se reemplaza la función `get_todos_los_maestros` por la nueva implementación; no se toca `app/main.py` (el router ya está registrado).

## Archivos a crear en tests

| Archivo | Descripción |
|---------|-------------|
| `tests/test_get_articulos_maestro.py` | Tests de integración con TestClient + SQLite en memoria |

---

## Diseño de schemas (`app/schemas/ApiResponseSchema.py`)

```python
class PagedResult(BaseModel, Generic[T]):
    items: List[T]
    totalItems: int
    pageNumber: int
    pageSize: int
    totalPages: int

class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
```

## Diseño de schemas (`app/schemas/ArticuloMaestroSchema.py`)

```python
class MedidaDto(BaseModel):
    id: int
    codigo: Optional[str]
    descripcion: Optional[str]

class SectorDto(BaseModel):
    id: int
    codigo: str
    descripcion: str

class FamiliaConSectorDto(BaseModel):
    id: int
    descripcion: str
    sector: Optional[SectorDto]

class SubFamiliaConJerarquiaDto(BaseModel):
    id: int
    descripcion: str
    familia: Optional[FamiliaConSectorDto]

class ArticuloPrecioConMedidaDto(BaseModel):
    id: int
    codigo: Optional[str]
    descripcion: Optional[str]
    precio1: float
    precio2: float
    precio3: float
    habilitado: bool
    medida: Optional[MedidaDto]   # del primer Articulo vinculado

class ArticuloMaestroDto(BaseModel):
    id: int
    codigo: Optional[str]
    descripcion: Optional[str]
    url_foto: Optional[str]
    activo: bool
    subfamilia: Optional[SubFamiliaConJerarquiaDto]   # del primer vínculo en la tabla intermedia
    variantes: List[ArticuloPrecioConMedidaDto]
```

---

## Diseño del Repository (`ArticuloMaestroRepository.obtener_paginado`)

La query tiene 3 pasos para evitar N+1:

**Paso 1 — Query principal (maestros + total)**
```sql
SELECT DISTINCT ArticuloMaestro.*
FROM ArticuloMaestro
[JOIN ArticuloMaestroXArticuloPrecio ON ... WHERE sectorId/familiaId/subfamiliaId]
WHERE [activo=true] AND [codigo ILIKE ...]
LIMIT pageSize OFFSET (pageNumber-1)*pageSize
```

**Paso 2 — Query de vínculos en batch**
```python
junction_records = db.query(ArticuloMaestroXArticuloPrecio)
    .options(
        joinedload(ArticuloMaestroXArticuloPrecio.subfamilia)
            .joinedload(SubFamilia.familia)
            .joinedload(Familia.sector),
        joinedload(ArticuloMaestroXArticuloPrecio.articulo_precio)
    )
    .filter(ArticuloMaestroXArticuloPrecio.articulo_maestro_id.in_(maestro_ids))
    .all()
```

Requiere agregar relationships a `ArticuloMaestroXArticuloPrecio`:
```python
subfamilia: Mapped["SubFamilia"] = relationship("SubFamilia", foreign_keys=[subfamilia_id], lazy="noload")
articulo_precio: Mapped["ArticuloPrecio"] = relationship("ArticuloPrecio", foreign_keys=[articulo_precio_id], lazy="noload")
```

**Paso 3 — Query de medidas en batch**
```python
# Obtener el primer Articulo por cada articulo_precio_id
subq = db.query(func.min(Articulo.id)).filter(
    Articulo.id_articulo_precio.in_(ap_ids)
).group_by(Articulo.id_articulo_precio).subquery()

articulos = db.query(Articulo).options(joinedload(Articulo.medida)).filter(Articulo.id.in_(subq)).all()
# primer_articulo_por_ap: dict[ap_id, Articulo]
```

**Ensamblado en servicio:**
```python
def _ensamblar_dto(maestro, junctions_por_maestro, primer_art_por_ap) -> ArticuloMaestroDto:
    mis_junctions = junctions_por_maestro.get(maestro.id, [])
    primer = mis_junctions[0] if mis_junctions else None
    variantes = [
        ArticuloPrecioConMedidaDto(
            ...j.articulo_precio,
            medida=primer_art_por_ap.get(j.articulo_precio_id).medida
        )
        for j in mis_junctions
    ]
    return ArticuloMaestroDto(
        ...,
        subfamilia=primer.subfamilia if primer else None,
        variantes=variantes
    )
```

---

## Diseño del Controller (en `ArticuloController.py`)

La función `get_todos_los_maestros` existente (rota) se reemplaza por:

```
Ruta: GET /articulos/maestro   (mismo router prefix /articulos, ya registrado en main.py)
Tag: Articulos (sin cambio)

Query params:
  pageNumber: int = Query(default=1, ge=1)
  pageSize: int = Query(default=20, ge=1, le=100)
  activo: Optional[bool] = Query(default=None)
  codigo: Optional[str] = Query(default=None)
  sectorId: Optional[int] = Query(default=None)
  familiaId: Optional[int] = Query(default=None)
  subfamiliaId: Optional[int] = Query(default=None)
Auth: obtener_usuario_confirmado
Returns: ApiResponse[PagedResult[ArticuloMaestroDto]]
```

Se elimina la función anterior y se escribe la nueva en su lugar. No se toca `app/main.py` (router ya registrado).

---

## Alternativa descartada

**Opción: crear un `ArticuloMaestroController.py` separado**

Separar el endpoint en su propio archivo de controller mantiene el principio de responsabilidad única y no toca el controller existente.

**Razón del descarte:** el dominio es el mismo (artículos), el controller `ArticuloController.py` ya gestiona toda la lógica de artículos y ya está registrado en `main.py`. Crear un controller extra solo para este endpoint añade fricción sin beneficio real. Al reemplazar la función rota en el controller existente, el código queda más limpio y no se necesita ningún cambio en `main.py`.

---

## Impacto en modelos existentes

`ArticuloMaestroXArticuloPrecio`: solo se agregan relationships opcionales (`lazy="noload"` para no cambiar comportamiento existente). No se toca la estructura de columnas ni los relationships existentes de `ArticuloMaestro` o `ArticuloPrecio`.
