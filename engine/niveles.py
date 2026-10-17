"""Nivel de aprobación: el más alto que exija cualquier revisión (R5.3, R5.5)."""
from .modelos import nivel_max
from .revisiones.montos import nivel_por_monto, monto_para_nivel  # noqa: F401  (reexporta)


def nivel_de_revisiones(revisiones) -> str:
    return nivel_max(*(r.nivel for r in revisiones))
