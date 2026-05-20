# Requirements — correccion_get_articulos_maestro

Feature ID: 2  
Estado: spec_ready

---

## Contexto

El endpoint `GET /articulos/maestro` filtra `ArticuloMaestro` por código,
sector, familia y subfamilia. Existen dos bugs independientes:

- **Bug 1 (codigo):** el filtro compara contra `ArticuloMaestro.codigo`
  en lugar de `ArticuloPrecio.codigo`, produciendo falsos positivos.
- **Bug 2 (sector/familia/subfamilia solos):** los JOINs se construyen en
  bloques `if` condicionales e independientes. Si solo `sector_id` está
  presente, el JOIN a `Familia` referencia `SubFamilia` que nunca fue
  joineada, causando un error SQL.

---

## Requisitos

**R1**
CUANDO el parámetro `codigo` está presente, el sistema DEBE filtrar
`ArticuloMaestro` retornando únicamente aquel cuyo campo `codigo` sea
igual exacto (case-insensitive) al valor indicado. Si no existe ningún
maestro con ese código, la lista devuelta estará vacía.

**R2**
CUANDO el parámetro `codigo` está presente, el sistema DEBE retornar
todas las variantes (`ArticulosPrecios`) vinculadas al maestro encontrado,
sin filtrar las variantes por código.

**R3**
CUANDO el parámetro `subfamiliaId` está presente, el sistema DEBE
retornar solo los `ArticuloMaestro` que tengan al menos una entrada en
`ArticuloMaestroXArticuloPrecio` con `subfamilia_id` igual al valor
indicado, sin errores SQL.

**R4**
CUANDO el parámetro `familiaId` está presente (con o sin `subfamiliaId`),
el sistema DEBE retornar solo los `ArticuloMaestro` cuya tabla intermedia
esté vinculada a una `SubFamilia` que pertenezca a la `Familia` indicada,
sin errores SQL.

**R5**
CUANDO el parámetro `sectorId` está presente (con o sin `familiaId` o
`subfamiliaId`), el sistema DEBE retornar solo los `ArticuloMaestro`
cuya tabla intermedia esté vinculada a una `SubFamilia` → `Familia` →
`Sector` que coincida con el `sectorId` indicado, sin errores SQL.

**R6**
CUANDO se combinan dos o más filtros (`codigo`, `sectorId`, `familiaId`,
`subfamiliaId`) de forma simultánea, el sistema DEBE aplicarlos en
conjunto (AND) y retornar solo los `ArticuloMaestro` que cumplan todos
los criterios, sin errores SQL.

**R7**
CUANDO no se proporciona ningún filtro de clasificación
(`sectorId`, `familiaId`, `subfamiliaId`, `codigo`), el sistema DEBE
retornar los `ArticuloMaestro` sin restringir por esos criterios (el
comportamiento preexistente no debe degradarse).
