# Blume API - Especificaciones Técnicas y Contexto

## 1. Descripción del Proyecto
API para un sistema de E-commerce y gestión textil (Blume ERP). Permite a los clientes navegar productos y generar presupuestos. Estos presupuestos son luego validados manualmente desde un ERP local para avanzar en el flujo comercial.

## 2. Stack Tecnológico
- **Lenguaje:** Python 3.10+
- **Framework Web:** FastAPI
- **Base de Datos:** MySQL (Intermedia)
- **ORM:** SQLAlchemy (Declarative Base)
- **Gestión de Imágenes:** Cloudinary
- **Generación de Documentos:** WeasyPrint (PDFs)
- **Frontend Asociado:** React + Vite

## 3. Arquitectura del Código
El proyecto sigue un patrón de diseño por capas para mantener el desacoplamiento:
1.  **Controllers:** Definen los endpoints (FastAPI Routers), manejan la entrada de datos y respuestas HTTP.
2.  **Services:** Contienen la lógica de negocio. Se definen mediante Interfaces (ABCs) e Implementaciones (`imp/`).
3.  **Repositories:** Manejan el acceso a datos y consultas SQLAlchemy. También definidos mediante Interfaces e Implementaciones.
4.  **Models:** Definición de tablas de la base de datos.
5.  **Schemas:** Modelos de Pydantic para validación y serialización de datos (DTOs).

## 4. Reglas de Negocio y Restricciones
- **Stock:** El sistema **NO** gestiona stock. La disponibilidad de los productos se maneja de forma externa o informativa, pero no hay lógica de decremento de inventario en esta API.
- **Flujo de Presupuestos:**
    - Los clientes generan un `Presupuesto`.
    - El estado inicial suele ser pendiente.
    - Un humano/administrador debe validar el presupuesto desde el ERP local.
    - El cambio de estado es manual y representa la aprobación comercial.
- **Usuarios:** 
    - Existen usuarios con perfiles de `Cliente`.
    - Los registros pueden requerir validación administrativa (`confirmado: False` por defecto).
    - Se utiliza baja lógica (`is_active: False`) en lugar de eliminar registros.
- **Imágenes:** Las fotos de artículos se suben a Cloudinary y se guarda la URL en la base de datos.

## 5. Convenciones de Desarrollo
- **Interfaces:** Siempre definir una interfaz en `app/services/I[Nombre]Service.py` o `app/repositories/I[Nombre]Repository.py` antes de implementar.
- **Inyección de Dependencias:** Se espera que los servicios reciban sus repositorios en el constructor (`__init__`).
- **Paginación:** Las consultas de listas deben usar el esquema `PagedResponse` para mantener la consistencia en el frontend.
- **Manejo de Errores:** Se deben capturar excepciones específicas y devolver respuestas claras al cliente.

## 6. Estructura de Datos Clave
- **Articulos / ArticuloPrecio:** Separación entre la entidad base del producto y su definición de precio/sector.
- **Familias / SubFamilias:** Jerarquía de categorización de productos.
- **Sectores:** Segmentación lógica de los productos.

---
*Este documento sirve como contexto para IAs. Cualquier sugerencia de código debe respetar esta estructura y restricciones.*