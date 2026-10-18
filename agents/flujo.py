"""Flujo del agente de entrada: recibir, preguntar, armar la ficha y llamar al motor.

El agente NO decide: entrega la ficha a engine.guardarrail.registrar_decision (EA6)."""
import logging
import os
from decimal import Decimal

from pydantic import ValidationError

from acta.estado import estado_publico, facturas_por_estado
from engine.contexto import contexto_desde_acta
from engine.guardarrail import registrar_decision
from engine.reglas_io import cargar_contexto_base, cargar_reglas, hoy_bogota, reglas_de_sala

from . import aclaraciones, archivo, ejemplos, id_tributaria, lectura_ia, segunda_lectura, xml_factura
from .estado import EstadoEntrada
from .seguridad import detectar_orden

log = logging.getLogger("entrada")

FACTURAS_MAX_DEFECTO = 5
FACTURAS_MAX_TOPE = 100


def facturas_max() -> int:
    """Facturas permitidas por sala. `FACTURAS_MAX` lo cambia; un valor inválido se ignora (EA1.5)."""
    try:
        valor = int(os.environ.get("FACTURAS_MAX", "").strip())
    except ValueError:
        return FACTURAS_MAX_DEFECTO
    return valor if 1 <= valor <= FACTURAS_MAX_TOPE else FACTURAS_MAX_DEFECTO
ORDEN_CAMPOS = ["monto", "beneficiario", "moneda", "vence", "numero"]


class EntradaRechazada(Exception):
    """Un motivo que sí se le puede decir al proveedor."""


def _agregar(chat, rol, texto):
    return chat + [[rol, texto]]


def _leer(tipo, datos, texto, clave_ejemplo, cliente):
    """(campos, modo). modo: xml | ia | guardada | regex. Ante cualquier falla, regex y dudosa (EA8)."""
    if tipo == "xml":                                    # lectura estructural, sin IA (EA10.2)
        try:
            return xml_factura.leer(datos), "xml"
        except xml_factura.XmlInvalido as e:
            raise EntradaRechazada(str(e)) from e
    if cliente is not None or lectura_ia.hay_clave():
        try:
            return lectura_ia.leer_con_ia(tipo, datos, texto, cliente), "ia"
        except lectura_ia.LecturaFallida as e:
            # Queda en los Logs del servidor (EA2b.9), sin ningún valor de clave.
            log.warning("La lectura con IA falló (%s): %s", lectura_ia.proveedor_activo(),
                        lectura_ia.sin_secretos(str(e))[:300])
    if clave_ejemplo in ejemplos.LECTURAS_GUARDADAS:
        return lectura_ia._limpiar(ejemplos.LECTURAS_GUARDADAS[clave_ejemplo]), "guardada"
    # Sin IA: solo patrones de texto, y la lectura queda dudosa (EA8.2).
    p = segunda_lectura.leer(texto)
    campos = {"beneficiario": p["beneficiario"], "numero": p["numero"], "monto": p["monto"],
              "moneda": p["moneda"], "vence": p["vence"].isoformat() if p["vence"] else None, "cuenta": None,
              "orden_compra": p["orden_compra"], "id_tributaria": p["id_tributaria"]}
    campos["dudosos"] = sorted(k for k, v in campos.items() if v is None and k not in ("cuenta", *lectura_ia.OPCIONALES))
    return campos, "regex"


def modo_demo() -> bool:
    return not lectura_ia.hay_clave()


def recibir(almacen, sala_id, nombre, datos, cliente=None, clave_ejemplo=None) -> dict:
    estados = EstadoEntrada(almacen)
    existentes = estados.listar(sala_id)
    limite = facturas_max()
    if len(existentes) >= limite:
        raise EntradaRechazada(f"Ya usaste las {limite} facturas permitidas en esta sala.")
    try:
        tipo = archivo.validar(nombre, datos)
    except archivo.ArchivoRechazado as e:
        raise EntradaRechazada(str(e)) from e
    texto = archivo.extraer_texto(tipo, datos)
    campos, modo = _leer(tipo, datos, texto, clave_ejemplo, cliente)
    if modo != "xml":                                    # EA10.7: el primer NIT con dígito del texto
        nit = id_tributaria.primer_nit(texto)
        if nit:
            if not campos.get("id_tributaria"):          # lo que ya leyó la IA o los patrones (OC3.2) manda
                campos["id_tributaria"] = f"{nit[0]}-{nit[1]}"
            campos["nit_dv"] = "correcto" if nit[2] else "incorrecto"
    if campos.get("nit_dv") == "incorrecto" or campos.get("cufe") == "falta":
        log.warning("Factura con identificación dudosa (NIT %s, CUFE %s): la lectura queda dudosa y se escala.",
                    campos.get("nit_dv") or "sin dato", campos.get("cufe") or "sin dato")

    if texto is None:
        segunda, difieren = "no_disponible", []                     # EA3.3
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
    ia_dudosa = (e["modo"] in ("regex",) or bool(L["dudosos"])
                 or L.get("nit_dv") == "incorrecto" or L.get("cufe") == "falta")      # EA10.5, EA10.6
    valores, origen = {}, {}
    for c in ("beneficiario", "numero", "monto", "moneda", "vence"):
        if L.get(c) in (None, ""):
            valores[c] = aclarados.get(c)
            origen[c] = "aclarado"                     # el original faltaba: el motor lo trata según R2.5
            ia_dudosa = True                           # y la lectura nunca queda como confiable
        else:
            valores[c] = str(L[c])
            origen[c] = "factura"
    return dict(
        factura_id=factura_id, beneficiario=valores["beneficiario"], numero=valores["numero"],
        monto=valores["monto"], moneda=valores["moneda"], vence=valores["vence"],
        recibida=hoy.isoformat(), cuenta_original=L.get("cuenta"), cuenta_aclarada=None,
        orden_compra=L.get("orden_compra"), id_tributaria=L.get("id_tributaria"),       # OC3.1: solo si la factura los trae
        valores_aclarados={k: v for k, v in aclarados.items()}, origen_campos=origen,
        lectura_ia="dudosa" if ia_dudosa or e["pendientes"] else "ok",
        segunda_lectura=e["segunda"],                  # el chat no puede cambiarla (EA5.4)
        orden_en_texto=e["orden_en_texto"], preparador=f"proveedor-{sala_id}")


def finalizar(almacen, sala_id, factura_id) -> dict:
    estados = EstadoEntrada(almacen)
    e = estados.obtener(sala_id, factura_id)
    hoy = hoy_bogota()
    ficha = construir_ficha(e, sala_id, factura_id, hoy)
    try:
        filas = almacen.filas(sala_id)
        reglas = reglas_de_sala(cargar_reglas(hoy)[0], filas)          # con los cambios de la sala (PP8.7)
        ctx = contexto_desde_acta(cargar_contexto_base(hoy), filas)
        registrar_decision(almacen, sala_id, ficha, ctx, reglas)
        registrada = facturas_por_estado(almacen.filas(sala_id))[factura_id]
        publico = estado_publico(registrada)
        if registrada.decision.get("ficha_invalida"):          # queda escalada y visible para finanzas (EA6.2)
            cierre = ("Gracias. No pude leer todos los datos de tu factura, así que quedó en revisión "
                      "manual de finanzas. Te avisaremos cuando haya una respuesta.")
        else:
            cierre = ("Gracias. Tu factura quedó resuelta." if publico == "resuelta"
                      else "Gracias. Tu factura quedó en revisión. Te avisaremos cuando haya una respuesta.")
    except (ValidationError, TypeError, ValueError):
        log.exception("No se pudo registrar la factura %s de la sala %s", factura_id, sala_id)
        cierre = "Hubo un problema al registrar tu factura. Por favor envíala de nuevo."
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
