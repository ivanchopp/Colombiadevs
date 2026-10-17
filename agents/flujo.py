"""Flujo del agente de entrada: recibir, preguntar, armar la ficha y llamar al motor.

El agente NO decide: entrega la ficha a engine.guardarrail.registrar_decision (EA6)."""
from decimal import Decimal

from pydantic import ValidationError

from acta.estado import estado_publico, facturas_por_estado
from engine.contexto import contexto_desde_acta
from engine.guardarrail import registrar_decision
from engine.reglas_io import cargar_contexto_base, cargar_reglas, hoy_bogota

from . import aclaraciones, archivo, ejemplos, lectura_ia, segunda_lectura
from .estado import EstadoEntrada
from .seguridad import detectar_orden

FACTURAS_MAX = 5
ORDEN_CAMPOS = ["monto", "beneficiario", "moneda", "vence", "numero"]


class EntradaRechazada(Exception):
    """Un motivo que sí se le puede decir al proveedor."""


def _agregar(chat, rol, texto):
    return chat + [[rol, texto]]


def _leer(tipo, datos, texto, clave_ejemplo, cliente):
    """(campos, modo). modo: ia | guardada | regex. Ante cualquier falla, regex y dudosa (EA8)."""
    if cliente is not None or lectura_ia.hay_clave():
        try:
            return lectura_ia.leer_con_ia(tipo, datos, texto, cliente), "ia"
        except lectura_ia.LecturaFallida:
            pass
    if clave_ejemplo in ejemplos.LECTURAS_GUARDADAS:
        return lectura_ia._limpiar(ejemplos.LECTURAS_GUARDADAS[clave_ejemplo]), "guardada"
    # Sin IA: solo patrones de texto, y la lectura queda dudosa (EA8.2).
    p = segunda_lectura.leer(texto)
    campos = {"beneficiario": p["beneficiario"], "numero": p["numero"], "monto": p["monto"],
              "moneda": p["moneda"], "vence": p["vence"].isoformat() if p["vence"] else None, "cuenta": None}
    campos["dudosos"] = sorted(k for k, v in campos.items() if v is None and k != "cuenta")
    return campos, "regex"


def modo_demo() -> bool:
    return not lectura_ia.hay_clave()


def recibir(almacen, sala_id, nombre, datos, cliente=None, clave_ejemplo=None) -> dict:
    estados = EstadoEntrada(almacen)
    existentes = estados.listar(sala_id)
    if len(existentes) >= FACTURAS_MAX:
        raise EntradaRechazada(f"Ya usaste las {FACTURAS_MAX} facturas permitidas en esta demo.")
    try:
        tipo = archivo.validar(nombre, datos)
    except archivo.ArchivoRechazado as e:
        raise EntradaRechazada(str(e)) from e
    texto = archivo.extraer_texto(tipo, datos)
    campos, modo = _leer(tipo, datos, texto, clave_ejemplo, cliente)

    if texto is None:
        segunda, difieren = "no_coincide", []                       # EA3.3
    else:
        segunda, difieren = segunda_lectura.comparar(campos, texto)
    dudosos = [c for c in ORDEN_CAMPOS if c in set(campos["dudosos"]) | set(difieren)]
    factura_id = f"F-{2001 + len(existentes)}"

    saludo = f"Recibí tu factura {campos.get('numero') or ''}.".replace("  ", " ")
    chat = _agregar([], "agente", saludo)
    estados.crear(
        sala_id, factura_id, estado="recibida", pendientes=dudosos, lectura=campos, aclarados={},
        chat=chat, texto=texto, nombre=nombre[:80], tipo=tipo, modo=modo, segunda=segunda,
        orden_en_texto=detectar_orden(texto))
    if dudosos:
        estados.actualizar(sala_id, factura_id, chat=_agregar(
            chat, "agente", "Tengo una duda. " + aclaraciones.pregunta_para(dudosos[0])))
        return estados.obtener(sala_id, factura_id)
    return finalizar(almacen, sala_id, factura_id)


def responder(almacen, sala_id, factura_id, mensaje: str) -> dict:
    estados = EstadoEntrada(almacen)
    e = estados.obtener(sala_id, factura_id)
    if e is None or e["estado"] != "recibida" or not e["pendientes"]:
        raise EntradaRechazada("Esta factura ya no espera respuestas.")
    mensaje = (mensaje or "").strip()
    if not mensaje:
        raise EntradaRechazada("Escribe un mensaje.")
    if len(mensaje) > aclaraciones.LARGO_MAX_MENSAJE:
        raise EntradaRechazada(f"El mensaje supera {aclaraciones.LARGO_MAX_MENSAJE} caracteres.")

    campo = e["pendientes"][0]
    chat = _agregar(e["chat"], "proveedor", mensaje)
    aclarados = dict(e["aclarados"])
    valor = aclaraciones.validar_respuesta(campo, mensaje)
    pendientes = list(e["pendientes"])
    if valor is not None:
        aclarados[campo] = str(valor)                  # se guarda aparte; nunca reemplaza el original (EA5.2)
        pendientes.pop(0)
    turnos = e["turnos"] + 1
    estados.actualizar(sala_id, factura_id, chat=chat, aclarados=aclarados, pendientes=pendientes,
                       turnos=turnos, orden_en_texto=e["orden_en_texto"] or detectar_orden(mensaje))
    if not pendientes or turnos >= aclaraciones.TURNOS_MAX:
        return finalizar(almacen, sala_id, factura_id)
    pregunta = aclaraciones.pregunta_para(pendientes[0])
    pre = "" if valor is not None else "No pude entender esa respuesta. "
    estados.actualizar(sala_id, factura_id, chat=_agregar(chat, "agente", pre + pregunta))
    return estados.obtener(sala_id, factura_id)


def construir_ficha(e: dict, sala_id: str, factura_id: str, hoy) -> dict:
    """Ficha con código. Lo aclarado va aparte y solo rellena lo que faltaba en el original (EA6.1)."""
    L, aclarados = e["lectura"], e["aclarados"]
    ia_dudosa = e["modo"] in ("regex",) or bool(L["dudosos"])
    valores = {}
    for c in ("beneficiario", "numero", "monto", "moneda", "vence"):
        if L.get(c) in (None, ""):
            valores[c] = aclarados.get(c)
            ia_dudosa = True                           # el original faltaba: nunca queda como lectura confiable
        else:
            valores[c] = str(L[c])
    return dict(
        factura_id=factura_id, beneficiario=valores["beneficiario"], numero=valores["numero"],
        monto=valores["monto"], moneda=valores["moneda"], vence=valores["vence"],
        recibida=hoy.isoformat(), cuenta_original=L.get("cuenta"), cuenta_aclarada=None,
        valores_aclarados={k: v for k, v in aclarados.items()},
        lectura_ia="dudosa" if ia_dudosa or e["pendientes"] else "ok",
        segunda_lectura=e["segunda"],                  # el chat no puede cambiarla (EA5.4)
        orden_en_texto=e["orden_en_texto"], preparador=f"proveedor-{sala_id}")


def finalizar(almacen, sala_id, factura_id) -> dict:
    estados = EstadoEntrada(almacen)
    e = estados.obtener(sala_id, factura_id)
    hoy = hoy_bogota()
    ficha = construir_ficha(e, sala_id, factura_id, hoy)
    try:
        reglas, _ = cargar_reglas(hoy)
        ctx = contexto_desde_acta(cargar_contexto_base(hoy), almacen.filas(sala_id))
        registrar_decision(almacen, sala_id, ficha, ctx, reglas)
        publico = estado_publico(facturas_por_estado(almacen.filas(sala_id))[factura_id])
        cierre = ("Gracias. Tu factura quedó resuelta." if publico == "resuelta"
                  else "Gracias. Tu factura quedó en revisión. Te avisaremos cuando haya una respuesta.")
    except (ValidationError, TypeError, ValueError):
        cierre = "Gracias. No pude leer todos los datos, así que tu factura quedó en revisión manual."
    estados.actualizar(sala_id, factura_id, estado="datos confirmados", pendientes=[],
                       chat=_agregar(e["chat"], "agente", cierre))
    return estados.obtener(sala_id, factura_id)


def estado_para_proveedor(almacen, sala_id, e: dict) -> str:
    """Estado público: del acta si ya hay decisión (EA7.2); si no, el de la entrada."""
    f = facturas_por_estado(almacen.filas(sala_id)).get(e["factura_id"])
    return estado_publico(f) if f else e["estado"] if e["estado"] != "datos confirmados" else "en revisión"


def recibir_ejemplo(almacen, sala_id, clave) -> dict:
    nombre, datos = ejemplos.leer_ejemplo(clave)
    return recibir(almacen, sala_id, nombre, datos, clave_ejemplo=clave)
