"""Escribir un evento: una transacción, idempotencia y huella (AC1)."""
import hashlib
import json
from datetime import datetime, timezone

from .almacen import Fila
from .huella import huella, huella_inicial, normalizar_payload

TIPOS = {"DECISION", "APROBACION", "RECHAZO", "CAMBIO_REGLA", "INTENTO_RECHAZADO",
         "REVISION_CONCILIACION", "CIERRE_PERIODO"}
LARGO_MAX_MOTIVO = 500


def clave_idempotencia(tipo, factura_id, payload) -> str:
    base = json.dumps([tipo, factura_id, payload], sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(base.encode()).hexdigest()


def ahora_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def escribir_evento(almacen, sala_id, tipo, factura_id, payload, actor, clave_idem=None) -> Fila:
    if tipo not in TIPOS:
        raise ValueError(f"tipo de evento no permitido: {tipo}")
    payload = normalizar_payload(payload)
    if isinstance(payload.get("motivo"), str) and len(payload["motivo"]) > LARGO_MAX_MOTIVO:
        raise ValueError("el motivo supera el largo máximo")
    clave = clave_idem or clave_idempotencia(tipo, factura_id, payload)
    with almacen.transaccion() as c:
        existente = almacen.buscar_por_clave(c, sala_id, clave)
        if existente:                                   # AC1.4
            return existente
        ultimo = almacen.ultima_fila(c, sala_id)
        num = ultimo.num + 1 if ultimo else 1
        anterior = ultimo.huella if ultimo else huella_inicial(sala_id)
        fila = Fila(sala_id, num, tipo, factura_id, payload, actor, clave, anterior, "", ahora_utc())
        fila.huella = huella(anterior, fila)
        almacen.insertar(c, fila)
        return fila
