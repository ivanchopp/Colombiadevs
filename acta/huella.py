"""Contenido canónico y huellas SHA-256 del acta.

Spec: specs/acta-y-csv (AC2.1, AC2.2). La huella no depende del idioma, de la zona horaria ni
del formato de la base de datos: todo se escribe en una forma única antes de calcularla.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

DOS_DECIMALES = Decimal("0.01")
SEIS_DECIMALES = Decimal("0.000001")


def texto_canonico(valor: Any) -> Any:
    """Convierte lo que JSON no entiende en texto estable (se usa como `default` de json.dumps)."""
    if isinstance(valor, Decimal):
        # Dos decimales si el valor es exacto con dos (montos); si no, seis (tasas).
        cuantizado = valor.quantize(DOS_DECIMALES)
        if cuantizado == valor:
            return format(cuantizado, "f")
        return format(valor.quantize(SEIS_DECIMALES), "f")
    if isinstance(valor, datetime):
        if valor.tzinfo is None:
            raise ValueError("las fechas con hora deben llevar zona horaria")
        return valor.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(valor, date):
        return valor.isoformat()
    raise TypeError(f"valor sin forma canónica: {type(valor).__name__}")


def contenido_canonico(fila: dict[str, Any]) -> bytes:
    """JSON con claves ordenadas, sin espacios y en UTF-8 (AC2.2)."""
    return json.dumps(
        fila, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=texto_canonico
    ).encode("utf-8")


def huella_inicial(sala_id: str) -> str:
    """Huella «anterior» de la primera fila de una sala (AC2.1)."""
    return hashlib.sha256(f"acta:{sala_id}".encode("utf-8")).hexdigest()


def huella(huella_anterior: str, fila: dict[str, Any]) -> str:
    """SHA-256 de la huella anterior más el contenido canónico de la fila (AC2.1)."""
    return hashlib.sha256(huella_anterior.encode("utf-8") + contenido_canonico(fila)).hexdigest()
