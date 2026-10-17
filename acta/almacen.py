"""Interfaz de almacenamiento del acta, con dos implementaciones (PostgreSQL y SQLite).

Spec: specs/acta-y-csv (AC1, AC7.1). Tarea AT1. Esqueleto: aún sin implementar.
"""
from __future__ import annotations

def abrir_almacen(*args, **kwargs):
    """Devuelve el almacén según DATABASE_URL (PostgreSQL) o el archivo local (SQLite)."""
    raise NotImplementedError("Tarea AT1: abrir_almacen")
