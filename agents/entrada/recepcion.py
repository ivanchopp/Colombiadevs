"""Recepción de archivos y mensajes. Spec: extracción (EX1). Tarea ET1.

Los límites son valores de demostración y salen de la configuración (app/config.py).
"""
from __future__ import annotations

TIPOS_PERMITIDOS: tuple[str, ...] = ("pdf", "jpg", "png", "eml", "txt")


def validar(archivo, sala_id: str):
    """Tipo por contenido, tamaño, páginas y límite por sala (EX1.1 a EX1.4)."""
    raise NotImplementedError("Tarea ET1: validar")
