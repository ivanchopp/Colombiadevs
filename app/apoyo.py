"""Funciones puras de apoyo a las pantallas. Sin Streamlit y sin lógica de decisión (PP7.1)."""
from decimal import Decimal

from acta.escribir import LARGO_MAX_MOTIVO, escribir_evento
from acta.estado import Factura, facturas_por_estado
from engine.guardarrail import AprobacionRechazada, validar_aprobacion
from engine.revisiones.calendario import estado_obligaciones
from engine.reglas_io import (EDITABLES, ErrorDeReglas, cambios_que_aflojan, cargar_contexto_base,
                              cargar_reglas, hoy_bogota, validar_cambio)

ROLES = {"PERSONA": "Persona de finanzas", "SENIOR": "Senior de finanzas"}
RANGO = {"NINGUNO": 0, "PERSONA": 1, "SENIOR": 2}
CANALES = [c.nombre for c in cargar_contexto_base(hoy_bogota()).canales]   # de data/canales.yaml
DECISIONES = {"PAGAR": "Pagar", "FRENAR": "Frenar", "ESCALAR": "Escalar"}


def formato_monto(valor, moneda: str) -> str:
    """9600000 -> '9.600.000 COP' (sin decimales si son cero)."""
    d = Decimal(str(valor))
    texto = f"{d:,.0f}" if d == d.to_integral() else f"{d:,.2f}"
    ent, _, dec = texto.partition(".")
    ent = ent.replace(",", ".")
    return f"{ent},{dec} {moneda}" if dec else f"{ent} {moneda}"


def quien_aprueba(f: Factura) -> str:
    if f.estado != "PENDIENTE":
        return ROLES.get((f.respuesta or {}).get("rol_clave", ""), "—")
    return ROLES.get(f.decision["nivel"], "—")


def cola_para_rol(facturas: dict[str, Factura], rol: str) -> list[Factura]:
    """PERSONA ve los de nivel persona; SENIOR ve también los de nivel senior (PP5.1)."""
    return [f for f in sorted(facturas.values(), key=lambda x: x.fila_decision)
            if f.estado == "PENDIENTE" and RANGO[f.decision["nivel"]] <= RANGO[rol]]


def _nivel_insuficiente(rol, factura):
    return RANGO[rol] < RANGO[factura.decision["nivel"]]


def responder(almacen, sala_id, factura: Factura, rol: str, aprobar: bool, motivo: str, canal=None):
    """Aprueba o rechaza una factura pendiente. Devuelve la fila escrita o lanza AprobacionRechazada.

    Solo se considera hecho si el acta confirma la escritura (PP5.6)."""
    actor = ROLES[rol]
    actual = facturas_por_estado(almacen.filas(sala_id)).get(factura.factura_id)
    if actual is None:
        raise AprobacionRechazada("La factura no existe en esta sala.")
    factura = actual                       # siempre se valida contra el estado vigente del acta
    try:
        if factura.estado != "PENDIENTE":
            raise AprobacionRechazada("La factura ya no está pendiente.")
        techo = cargar_reglas(hoy_bogota())[0].techo_duro_pago
        validar_aprobacion(rol, factura.decision["nivel"], motivo, actor,
                           factura.decision.get("preparador"), factura.monto_base if aprobar else Decimal("0"),
                           techo)
        if aprobar and canal not in CANALES:
            raise AprobacionRechazada("Elige un canal de pago.")
    except AprobacionRechazada as e:
        if _nivel_insuficiente(rol, factura) or "techo" in str(e):
            escribir_evento(almacen, sala_id, "INTENTO_RECHAZADO", factura.factura_id,
                            {"intento": "APROBACION" if aprobar else "RECHAZO", "regla": str(e),
                             "motivo": (motivo or "")[:LARGO_MAX_MOTIVO]}, actor)
        raise
    payload = {"decision_fila": factura.fila_decision, "rol": actor, "rol_clave": rol,
               "motivo": motivo.strip()}
    if aprobar:
        payload["canal_elegido"] = canal
        payload["pago_de_practica"] = True
    # Una sola respuesta por decisión, aunque lleguen dos clics a la vez.
    return escribir_evento(almacen, sala_id, "APROBACION" if aprobar else "RECHAZO",
                           factura.factura_id, payload, actor,
                           clave_idem=f"respuesta:{factura.factura_id}:{factura.fila_decision}")


def estados_calendario(ctx, reglas):
    """Estado de cada obligación, calculado por el motor (R6.4)."""
    return [{"proveedor": o.beneficiario, "fecha": o.fecha, "monto": o.monto_base, "estado": e}
            for o, e in estado_obligaciones(ctx, reglas)]


def inesperadas(facturas: dict[str, Factura]) -> list[Factura]:
    return [f for f in facturas.values()
            if any(r["regla"] == "R6.2" for r in f.decision.get("revisiones", []))]


def cambiar_reglas(almacen, sala_id, actuales, valores: dict, rol: str, motivo: str):
    """Confirma un cambio de reglas en la sala (PP8.4 a PP8.6). Lanza ErrorDeReglas si no procede.

    Solo el senior firma lo que afloja; si lo intenta la persona, queda un INTENTO_RECHAZADO."""
    nuevas = validar_cambio(actuales, valores)
    aflojan = cambios_que_aflojan(actuales, nuevas)
    if not any(getattr(nuevas, k) != getattr(actuales, k) for k in EDITABLES):
        raise ErrorDeReglas("No hay cambios.")
    if not (motivo or "").strip():
        raise ErrorDeReglas("Escribe un motivo: es obligatorio.")
    if len(motivo) > LARGO_MAX_MOTIVO:
        raise ErrorDeReglas(f"El motivo supera {LARGO_MAX_MOTIVO} caracteres.")
    if aflojan and rol != "SENIOR":
        escribir_evento(almacen, sala_id, "INTENTO_RECHAZADO", None,
                        {"intento": "CAMBIO_REGLA", "regla": "R9.4: aflojar exige la firma del senior",
                         "aflojan": aflojan, "motivo": motivo.strip()}, ROLES[rol])
        raise ErrorDeReglas("Este cambio afloja una regla: solo el senior de finanzas puede firmarlo.")
    payload = {"antes": {k: str(getattr(actuales, k)) for k in EDITABLES},
               "despues": {k: str(getattr(nuevas, k)) for k in EDITABLES},
               "version_anterior": actuales.version, "afloja": bool(aflojan), "aflojan": aflojan,
               "pedido_por": ROLES[rol], "firmado_por": ROLES[rol] if aflojan else None,
               "vigente_desde": hoy_bogota().isoformat(), "motivo": motivo.strip()}
    return escribir_evento(almacen, sala_id, "CAMBIO_REGLA", None, payload, ROLES[rol])
