"""Funciones puras de apoyo a las pantallas. Sin Streamlit y sin lógica de decisión (PP7.1)."""
from datetime import date
from decimal import Decimal

from acta.escribir import LARGO_MAX_MOTIVO, escribir_evento
from acta.estado import Factura, facturas_por_estado

ROLES = {"PERSONA": "Persona de finanzas", "SENIOR": "Senior de finanzas"}
RANGO = {"NINGUNO": 0, "PERSONA": 1, "SENIOR": 2}
TECHO_DURO_PAGO = Decimal("50000000")        # supuesto, tomado de AVANCES.md
CANALES = ["Bre-B", "PSE", "USDC", "ACH en USD", "Wire en USD"]   # supuesto
DECISIONES = {"PAGAR": "Pagar", "FRENAR": "Frenar", "ESCALAR": "Escalar"}


class AprobacionRechazada(Exception):
    pass


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


def validar_aprobacion(rol: str, factura: Factura, motivo: str, actor: str) -> None:
    """Provisional hasta que exista engine/guardarrail.py (T9). Cubre PP5.2 a PP5.4."""
    if factura.estado != "PENDIENTE":
        raise AprobacionRechazada("La factura ya no está pendiente.")
    if RANGO[rol] < RANGO[factura.decision["nivel"]]:
        raise AprobacionRechazada("Tu rol no alcanza el nivel que exige este caso.")
    if not (motivo or "").strip():
        raise AprobacionRechazada("Escribe un motivo: es obligatorio.")
    if len(motivo) > LARGO_MAX_MOTIVO:
        raise AprobacionRechazada(f"El motivo supera {LARGO_MAX_MOTIVO} caracteres.")
    if actor == factura.decision.get("preparador"):
        raise AprobacionRechazada("Quien preparó el caso no puede aprobarlo.")


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
        validar_aprobacion(rol, factura, motivo, actor)
        if aprobar and factura.monto_base > TECHO_DURO_PAGO:
            raise AprobacionRechazada("El monto supera el techo duro de pago.")
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


def estados_calendario(calendario, facturas: dict[str, Factura], hoy: date):
    """Estado de cada obligación: llegó, pendiente o atrasada (PP6.2)."""
    salida = []
    for prov, fecha, monto, fid in calendario:
        if fid and fid in facturas:
            estado = "llegó"
        elif fecha < hoy:
            estado = "atrasada"
        else:
            estado = "pendiente"
        salida.append({"proveedor": prov, "fecha": fecha, "monto": monto, "estado": estado})
    return salida


def inesperadas(facturas: dict[str, Factura]) -> list[Factura]:
    return [f for f in facturas.values()
            if any(r["regla"] == "R6.2" for r in f.decision.get("revisiones", []))]
