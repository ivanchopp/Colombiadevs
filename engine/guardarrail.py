"""Guardarraíl: nada se escribe como pago si el motor no lo permite (R8)."""
from decimal import Decimal

from pydantic import ValidationError

from acta.escribir import LARGO_MAX_MOTIVO, escribir_evento

from .evaluar import asociar_beneficiario, evaluar
from .modelos import RANGO, Ficha


class DecisionRechazada(Exception):
    pass


class AprobacionRechazada(Exception):
    pass


def payload_decision(ficha, resultado, ctx) -> dict:
    f = ficha if isinstance(ficha, Ficha) else Ficha.model_validate(ficha)
    f = asociar_beneficiario(f, ctx)                       # el acta lleva el nombre registrado (R4.4)
    reg = ctx.registros.get(f.beneficiario)
    canal = resultado.canal
    return {
        "factura_id": f.factura_id, "beneficiario": f.beneficiario, "pais": reg.pais if reg else "",
        "numero": f.numero, "monto": f.monto, "moneda": f.moneda,
        "monto_base": resultado.monto_base if resultado.monto_base is not None else Decimal("0"),
        "tasa": str(resultado.tasa_usada) if resultado.tasa_usada is not None else "",
        "decision": resultado.decision, "nivel": resultado.nivel,
        "revisiones": [r.model_dump(mode="json") for r in resultado.revisiones],
        "motivo": resultado.motivo, "version_reglas": resultado.version_reglas,
        "canal_sugerido": canal.sugerido if canal else None,
        "canales": [c.model_dump(mode="json") for c in canal.evaluados] if canal else [],
        "aviso_canal": canal.aviso if canal else None,
        "preparador": f.preparador, "vence": f.vence, "recibida": f.recibida,
        "obligacion_id": resultado.obligacion_id, "periodo": ctx.periodo,
        "ficha": f.model_dump(mode="json"), "supuesto": True,
    }


def payload_ficha_invalida(ficha: dict, resultado, ctx) -> dict:
    """DECISION de una ficha que no cumple el esquema (R2.1, R8.6): escalada, sin datos de pago."""
    def texto(clave, defecto, largo=80):
        v = ficha.get(clave)
        return str(v).strip()[:largo] if v not in (None, "") else defecto
    return {
        "factura_id": str(ficha["factura_id"]), "beneficiario": texto("beneficiario", "(sin leer)"), "pais": "",
        "numero": texto("numero", "(sin leer)", 40), "monto": "0.00", "moneda": "N/D", "monto_base": "0.00",
        "tasa": "", "decision": resultado.decision, "nivel": resultado.nivel,
        "revisiones": [r.model_dump(mode="json") for r in resultado.revisiones],
        "motivo": resultado.motivo, "version_reglas": resultado.version_reglas,
        "canal_sugerido": None, "canales": [], "aviso_canal": None,
        "preparador": texto("preparador", "desconocido"), "vence": "", "recibida": texto("recibida", ""),
        "obligacion_id": None, "periodo": ctx.periodo, "ficha": {k: str(v)[:200] for k, v in ficha.items()},
        "ficha_invalida": True, "campos_con_problema": resultado.revisiones[0].observado, "supuesto": True,
    }


def registrar_decision(almacen, sala_id, ficha, ctx, reglas, propuesto=None, actor="Motor de reglas"):
    """Revalida todo antes de escribir (R8.1). Una ficha inválida se registra como escalada (R8.6)."""
    recalculado = evaluar(ficha, ctx, reglas)
    try:
        f = ficha if isinstance(ficha, Ficha) else Ficha.model_validate(ficha)
    except ValidationError:
        if not isinstance(ficha, dict) or not ficha.get("factura_id"):
            raise                                   # sin factura_id no hay a qué ligar el caso
        if propuesto is not None and propuesto.decision == "PAGAR":
            escribir_evento(almacen, sala_id, "INTENTO_RECHAZADO", str(ficha["factura_id"]),
                            {"intento": "PAGAR", "regla": "Intento de pagar con la ficha inválida",
                             "decision_real": recalculado.decision, "motivo": recalculado.motivo}, actor)
            raise DecisionRechazada("intento de pagar con la ficha inválida")
        return escribir_evento(almacen, sala_id, "DECISION", str(ficha["factura_id"]),
                               payload_ficha_invalida(ficha, recalculado, ctx), actor)
    if propuesto is not None and propuesto.decision == "PAGAR" and recalculado.decision != "PAGAR":
        escribir_evento(almacen, sala_id, "INTENTO_RECHAZADO", f.factura_id,
                        {"intento": "PAGAR", "regla": "Intento de pagar fuera de las reglas",
                         "decision_real": recalculado.decision, "motivo": recalculado.motivo}, actor)
        raise DecisionRechazada("intento de pagar fuera de las reglas")
    return escribir_evento(almacen, sala_id, "DECISION", f.factura_id,
                           payload_decision(f, recalculado, ctx), actor)


def validar_aprobacion(rol, nivel_exigido, motivo, actor, preparador, monto_base, techo,
                       ficha_invalida=False, aprobar=True):
    """Rol suficiente, motivo, separación de funciones, techo duro y ficha válida (R8.2, R8.3, R8.6)."""
    if ficha_invalida and aprobar:
        raise AprobacionRechazada("La ficha no tiene los datos obligatorios: no se puede aprobar. "
                                  "Solo se puede rechazar.")
    if RANGO[rol] < RANGO[nivel_exigido]:
        raise AprobacionRechazada("Tu rol no alcanza el nivel que exige este caso.")
    if not (motivo or "").strip():
        raise AprobacionRechazada("Escribe un motivo: es obligatorio.")
    if len(motivo) > LARGO_MAX_MOTIVO:
        raise AprobacionRechazada(f"El motivo supera {LARGO_MAX_MOTIVO} caracteres.")
    if actor == preparador:
        raise AprobacionRechazada("Quien preparó el caso no puede aprobarlo.")
    if monto_base > techo:
        raise AprobacionRechazada("El monto supera el techo duro de pago.")
