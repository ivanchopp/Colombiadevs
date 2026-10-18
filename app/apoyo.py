"""Funciones puras de apoyo a las pantallas. Sin Streamlit y sin lógica de decisión (PP7.1)."""
from decimal import Decimal

from acta.escribir import LARGO_MAX_MOTIVO, escribir_evento
from acta.estado import Factura, facturas_por_estado
from engine.compras import normalizar_oc, proveedor_por_id
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


def monto_legible(d: dict) -> str:
    """Monto de una decisión para pantalla; «sin leer» si la ficha era inválida (PP4.2)."""
    return "sin leer" if d.get("ficha_invalida") else formato_monto(d["monto"], d["moneda"])


def quien_aprueba(f: Factura) -> str:
    if f.estado != "PENDIENTE":
        return ROLES.get((f.respuesta or {}).get("rol_clave", ""), "—")
    return ROLES.get(f.decision["nivel"], "—")


def cola_para_rol(facturas: dict[str, Factura], rol: str) -> list[Factura]:
    """PERSONA ve los de nivel persona; SENIOR ve también los de nivel senior (PP5.1)."""
    return [f for f in sorted(facturas.values(), key=lambda x: x.fila_decision)
            if f.estado == "PENDIENTE" and RANGO[f.decision["nivel"]] <= RANGO[rol]]


def pendientes_por_rol(facturas: dict[str, Factura]) -> dict[str, int]:
    """Aprobaciones pendientes que le tocan a cada rol según el nivel que exige la decisión (PP3.3).
    No cuenta las de ficha inválida: solo se pueden rechazar (PP5.7)."""
    cuenta = {"PERSONA": 0, "SENIOR": 0}
    for f in facturas.values():
        if f.estado == "PENDIENTE" and not f.decision.get("ficha_invalida") and f.decision["nivel"] in cuenta:
            cuenta[f.decision["nivel"]] += 1
    return cuenta


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
                           techo, ficha_invalida=bool(factura.decision.get("ficha_invalida")), aprobar=aprobar)
        if aprobar and canal not in CANALES:
            raise AprobacionRechazada("Elige un canal de pago.")
    except AprobacionRechazada as e:
        if _nivel_insuficiente(rol, factura) or "techo" in str(e) or "no se puede aprobar" in str(e):
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


ESTADO_FACTURA = {"PAGADA": "pagada", "PENDIENTE": "escalada", "FRENADA": "frenada", "RECHAZADA": "rechazada"}
ADVERTENCIA_OC = {"no_coincide_con_proveedor": "la identificación de la orden no coincide con la del proveedor"}


def ordenes_con_estado(ctx, facturas: dict[str, Factura]) -> list[dict]:
    """Una fila por orden de compra para la página de órdenes (PP9.1). El estado lo calcula el motor (OC5)."""
    filas = []
    for clave, oc in sorted(ctx.ordenes.items(), key=lambda kv: kv[1].numero):
        prov = proveedor_por_id(ctx, oc.proveedor_id)
        usada = ctx.oc_facturadas.get(clave)
        f = facturas.get(usada) if usada else None
        filas.append({
            "numero": oc.numero, "proveedor": prov.nombre if prov else "(proveedor no encontrado)",
            "articulo": oc.articulo, "total": formato_monto(oc.total, oc.moneda),
            "estado": "facturada" if usada else "abierta", "factura": usada or "—",
            "estado_factura": ESTADO_FACTURA.get(f.estado, f.estado) if f else "—",
            "advertencia": "; ".join(ADVERTENCIA_OC.get(m, m) for m in oc.marcas) or "—"})
    return filas


def oc_de_factura(factura: Factura, ctx) -> dict | None:
    """La orden que cita una factura y el resultado de la revisión OC4, para el detalle (PP9.3)."""
    numero = (factura.decision.get("ficha") or {}).get("orden_compra")
    if not numero:
        return None
    revision = [r for r in factura.decision.get("revisiones", []) if r["regla"].startswith("OC")]
    resultado = " · ".join(f"{r['resultado']}: {r['mensaje']}" for r in revision) or "sin revisión registrada"
    oc = ctx.ordenes.get(normalizar_oc(numero))
    if oc is None:
        return {"numero": numero, "existe": False, "resultado": resultado}
    prov = proveedor_por_id(ctx, oc.proveedor_id)
    usada = ctx.oc_facturadas.get(normalizar_oc(oc.numero))
    return {"numero": oc.numero, "existe": True, "proveedor": prov.nombre if prov else "(proveedor no encontrado)",
            "total": formato_monto(oc.total, oc.moneda), "estado": "facturada" if usada else "abierta",
            "resultado": resultado}


def cambiar_reglas(almacen, sala_id, actuales, valores: dict, rol: str, motivo: str,
                   origen: str = "formulario", pedido: str | None = None):
    """Confirma un cambio de reglas en la sala (PP8.4 a PP8.6). Lanza ErrorDeReglas si no procede.

    Solo el senior firma lo que afloja; si lo intenta la persona, queda un INTENTO_RECHAZADO.
    `origen="texto"` guarda el pedido original como dato (AR4); nunca se obedece ni se reenvía a la IA."""
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
               "vigente_desde": hoy_bogota().isoformat(), "motivo": motivo.strip(),
               "origen": "texto" if origen == "texto" else "formulario"}
    if origen == "texto":
        payload["pedido"] = (pedido or "")[:500]
    return escribir_evento(almacen, sala_id, "CAMBIO_REGLA", None, payload, ROLES[rol])
