"""Monto, moneda, fecha y nombres en formas comparables.

Spec: specs/extraccion-y-agente-de-entrada (EX2.4, EX2.5). Tarea ET3. Esqueleto: aún sin implementar.
"""
from __future__ import annotations

def normalizar_monto(*args, **kwargs):
    """Entiende los formatos en español y en inglés; lo ambiguo queda como dudoso."""
    raise NotImplementedError("Tarea ET3: normalizar_monto")

def normalizar_moneda(*args, **kwargs):
    """Código ISO 4217; un «$» solo es ambiguo."""
    raise NotImplementedError("Tarea ET3: normalizar_moneda")

def normalizar_fecha(*args, **kwargs):
    """ISO 8601; lo ambiguo queda como dudoso."""
    raise NotImplementedError("Tarea ET3: normalizar_fecha")

def normalizar_nombre(*args, **kwargs):
    """Mayúsculas, sin tildes ni puntuación."""
    raise NotImplementedError("Tarea ET3: normalizar_nombre")
