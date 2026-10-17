"""Estado de cada factura, calculado desde el acta, y estado público para el Panel 1.

Spec: specs/acta-y-csv (AC4). Tarea AT4. Esqueleto: aún sin implementar.
"""
from __future__ import annotations

def estado_por_factura(*args, **kwargs):
    """PAGADA, FRENADA, PENDIENTE o RECHAZADA, según el último evento (AC4.1)."""
    raise NotImplementedError("Tarea AT4: estado_por_factura")

def estado_publico(*args, **kwargs):
    """Solo «en revisión» o «resuelta»; nunca motivos, reglas ni montos (AC4.3)."""
    raise NotImplementedError("Tarea AT4: estado_publico")
