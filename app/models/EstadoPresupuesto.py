from enum import Enum


class EstadoPresupuesto(Enum):
    CREADO = "creado"
    VALIDADO = "validado"
    ELIMINADO = "eliminado"