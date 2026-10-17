"""Contenido canónico y huella SHA-256 de cada fila (AC2.1, AC2.2)."""
import hashlib
import json
from datetime import date, datetime
from decimal import Decimal


def texto_canonico(valor):
    if isinstance(valor, Decimal):
        return f"{valor:.2f}"
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    raise TypeError(f"valor no serializable: {type(valor)!r}")


def normalizar_payload(payload: dict) -> dict:
    """Pasa por JSON para que lo guardado y lo hasheado sean idénticos."""
    return json.loads(json.dumps(payload, default=texto_canonico, ensure_ascii=False))


def contenido_canonico(fila) -> bytes:
    cuerpo = {
        "sala_id": fila.sala_id,
        "num": fila.num,
        "tipo": fila.tipo,
        "factura_id": fila.factura_id,
        "payload": fila.payload,
        "actor": fila.actor,
        "creado_en": fila.creado_en,
    }
    return json.dumps(cuerpo, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, default=texto_canonico).encode("utf-8")


def huella(huella_anterior: str, fila) -> str:
    return hashlib.sha256(huella_anterior.encode() + contenido_canonico(fila)).hexdigest()


def huella_inicial(sala_id: str) -> str:
    return hashlib.sha256(f"acta:{sala_id}".encode()).hexdigest()
