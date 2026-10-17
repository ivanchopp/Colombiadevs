"""Guardarraíl: nada se escribe como pago si el motor no lo permite (R8)."""
from decimal import Decimal

from acta.escribir import LARGO_MAX_MOTIVO, escribir_evento

from .evaluar import evaluar
from .modelos import RANGO, Ficha


class DecisionRechazada(Exception):
    pass


class AprobacionRechazada(Exception):
    pass


def payload_decision(ficha, resultado, ctx) -> dict:
    f = ficha if isinstance(ficha, Ficha) else Ficha.model_validate(ficha)
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


def registrar_decision(almacen, sala_id, ficha, ctx, reglas, propuesto=None, actor="Motor de reglas"):
    """Revalida todo antes de escribir (R8.1). Una ficha inválida no se registra."""
    recalculado = evaluar(ficha, ctx, reglas)
    f = ficha if isinstance(ficha, Ficha) else Ficha.model_validate(ficha)   # lanza si es inválida
    if propuesto is not None and propuesto.decision == "PAGAR" and recalculado.decision != "PAGAR":
        escribir_evento(almacen, sala_id, "INTENTO_RECHAZADO", f.factura_id,
                        {"intento": "PAGAR", "regla": "Intento de pagar fuera de las reglas",
                         "decision_real": recalculado.decision, "motivo": recalculado.motivo}, actor)
        raise DecisionRechazada("intento de pagar fuera de las reglas")
    return escribir_evento(almacen, sala_id, "DECISION", f.factura_id,
                           payload_decision(f, recalculado, ctx), actor)


def validar_aprobacion(rol, nivel_exigido, motivo, actor, preparador, monto_base, techo):
    """Rol suficiente, motivo, separación de funciones y techo duro (R8.2, R8.3)."""
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
