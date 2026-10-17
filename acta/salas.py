"""Códigos de sala. Spec: specs/acta-y-csv (AC7) y paneles-y-despliegue (PD2).

Pendiente: crear, reiniciar y purgar salas en la base de datos (tarea AT7).
"""
from __future__ import annotations

import secrets

# Sin caracteres que se confunden (0/O, 1/I).
ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generar_codigo(largo: int = 8) -> str:
    """Código aleatorio y sin datos personales (AC7)."""
    return "".join(secrets.choice(ALFABETO) for _ in range(largo))


def codigo_valido(codigo: str | None, largo: int = 8) -> bool:
    """Solo comprueba el formato. Que la sala exista se comprueba contra la base (AT7)."""
    return bool(codigo) and len(codigo) == largo and all(c in ALFABETO for c in codigo)
