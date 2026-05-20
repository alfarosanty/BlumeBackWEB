# Tasks — get_articulos_maestro

> El implementer marca `[x]` al completar cada task. El reviewer rechaza si queda `[ ]` sin justificación.

---

- [x] T1 — Crear `app/schemas/ApiResponseSchema.py` con `PagedResult[T]` y `ApiResponse[T]`. Cubre: R9.

- [x] T2 — Crear `app/schemas/ArticuloMaestroSchema.py` con los DTOs: `MedidaDto`, `SectorDto`, `FamiliaConSectorDto`, `SubFamiliaConJerarquiaDto`, `ArticuloPrecioConMedidaDto`, `ArticuloMaestroDto`. Cubre: R8, R10.

- [x] T3 — Modificar `app/models/ArticuloMaestroXArticuloPrecio.py`: agregar relationships `subfamilia` (→ SubFamilia) y `articulo_precio` (→ ArticuloPrecio) con `lazy="select"` y `overlaps="maestros,variantes"`. Cubre: R8 (precondición de la query).

- [x] T4 — Crear `app/repositories/IArticuloMaestroRepository.py` con la interface ABC y los métodos `obtener_paginado`, `obtener_junctions_con_detalle`, `obtener_primer_articulo_por_ap`. Cubre: R4, R5, R6.

- [x] T5 — Crear `app/repositories/imp/ArticuloMaestroRepository.py` con la implementación en 3 pasos: (a) query principal con filtros, (b) query batch de vínculos con subfamilia/AP, (c) query batch de primer Articulo por AP para Medida. Cubre: R4, R5, R6, R8, R10.

- [x] T6 — Actualizar `app/services/IArticuloMaestroService.py`: agregar método abstracto `obtener_paginado(...)` que retorna `tuple[int, list[ArticuloMaestroDto]]`. Cubre: R8, R9.

- [x] T7 — Crear `app/services/imp/ArticuloMaestroService.py`: implementar `obtener_paginado()` que llama al repository, ensambla los DTOs y retorna `(total, list[ArticuloMaestroDto])`. Cubre: R8, R10.

- [x] T8 — En `app/controllers/ArticuloController.py`: reemplazar la función rota por la nueva implementación con query params `pageNumber`, `pageSize`, `activo`, `codigo`, `sectorId`, `familiaId`, `subfamiliaId`, auth `obtener_usuario_confirmado`, y response `ApiResponse[PagedResult[ArticuloMaestroDto]]`. No se tocó `app/main.py`. Cubre: R1, R2, R3, R6, R7, R9.

- [x] T9 — Escribir `tests/test_get_articulos_maestro.py` con los 9 tests cubriendo R1–R10. Todos pasan (9/9 ✓).
