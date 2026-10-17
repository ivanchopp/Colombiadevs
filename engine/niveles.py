"""Nivel de aprobación según el monto. Spec: motor-de-reglas (R5.3, R5.5)."""
from __future__ import annotations

from decimal import Decimal

from engine.modelos import Nivel, Reglas

ORDEN: dict[str, int] = {"NINGUNO": 0, "PERSONA": 1, "SENIOR": 2}


def nivel_por_monto(monto_para_nivel: Decimal, reglas: Reglas) -> Nivel:
    """NINGUNO hasta `autopago_max`, PERSONA hasta `persona_max`, SENIOR por encima (R5.3)."""
    if monto_para_nivel <= reglas.autopago_max:
        return "NINGUNO"
    if monto_para_nivel <= reglas.persona_max:
        return "PERSONA"
    return "SENIOR"


def nivel_maximo(niveles: list[Nivel]) -> Nivel:
    """Cuando varias revisiones exigen niveles distintos, gana el más alto (R5.5)."""
    return max(niveles, key=lambda n: ORDEN[n], default="NINGUNO")
