"""Verificar la cadena de huellas (AC2.3)."""
from dataclasses import dataclass

from .huella import huella, huella_inicial


@dataclass
class ResultadoCadena:
    correcta: bool
    filas: int
    primera_fila_mala: int | None = None


def verificar_cadena(almacen, sala_id) -> ResultadoCadena:
    anterior = huella_inicial(sala_id)
    esperado = 1
    filas = almacen.filas(sala_id)
    for f in filas:
        if f.num != esperado or f.huella_anterior != anterior or f.huella != huella(anterior, f):
            return ResultadoCadena(False, len(filas), f.num)
        anterior, esperado = f.huella, esperado + 1
    return ResultadoCadena(True, len(filas))
