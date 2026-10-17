"""Salas de demo: un código por visitante (AC7)."""
import re
import secrets

from data.demo_semilla import eventos_semilla

from .escribir import escribir_evento

ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"   # sin 0/O/1/I
PATRON = re.compile(r"^[A-HJ-NP-Z2-9]{8}$")


def codigo_valido(codigo) -> bool:
    return isinstance(codigo, str) and PATRON.match(codigo) is not None


def crear(almacen) -> str:
    """Crea una sala nueva con los datos de ejemplo (AC7.3)."""
    sala = "".join(secrets.choice(ALFABETO) for _ in range(8))
    for tipo, factura_id, payload, actor in eventos_semilla():
        escribir_evento(almacen, sala, tipo, factura_id, payload, actor)
    return sala
