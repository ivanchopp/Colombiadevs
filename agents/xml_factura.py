"""Lectura estructural de la factura electrónica en XML de varios países, sin IA (EA10, EA11, EA12).

UBL 2.1 (Colombia, Perú) y CFDI (México) tienen su lectura propia; los demás formatos salen de la tabla FORMATOS.
La segunda lectura del XML es otro método, por patrones de texto (`segunda_lectura.leer_xml`)."""
import re
import xml.etree.ElementTree as ET
from decimal import Decimal

from . import id_tributaria

PELIGROSO = re.compile(rb"<!\s*(DOCTYPE|ENTITY)", re.I)


class XmlInvalido(Exception):
    pass


class FormatoDesconocido(XmlInvalido):
    """XML bien formado de un formato que no está en la tabla: se lee como texto y se escala (EA12.7)."""


# EA12.1 (EA11 es el CFDI de México, con su lectura propia): por campo, rutas alternativas. «+» une partes con «-».
FORMATOS = [
    {"nombre": "SRI (Ecuador)", "raices": ("factura",), "beneficiario": ["infoTributaria/razonSocial"],
     "numero": ["infoTributaria/estab+infoTributaria/ptoEmi+infoTributaria/secuencial"],
     "monto": ["infoFactura/importeTotal"], "moneda": ["infoFactura/moneda"], "vence": [], "id": ["infoTributaria/ruc"]},
    {"nombre": "CFE (Uruguay)", "raices": ("CFE",), "beneficiario": ["Emisor/RznSoc"], "numero": ["IdDoc/Serie+IdDoc/Nro"],
     "monto": ["Totales/MntPagar", "Totales/MntTotal"], "moneda": ["Totales/TpoMoneda"], "vence": ["IdDoc/FchVenc"],
     "id": ["Emisor/RUCEmisor"]},
    {"nombre": "NF-e (Brasil)", "raices": ("nfeProc", "NFe"), "beneficiario": ["emit/xNome"], "numero": ["ide/serie+ide/nNF"],
     "monto": ["ICMSTot/vNF"], "moneda": [], "moneda_defecto": "BRL", "vence": ["dup/dVenc"], "id": ["emit/CNPJ", "emit/CPF"]},
    # shortcut: de un EnvioDTE con varias facturas solo se lee la primera (DE5); subir una por archivo.
    {"nombre": "DTE (Chile)", "raices": ("DTE", "EnvioDTE"), "beneficiario": ["Emisor/RznSoc"], "numero": ["IdDoc/Folio"],
     "monto": ["Totales/MntTotal"], "moneda": [], "moneda_defecto": "CLP", "vence": ["IdDoc/FchVenc"], "id": ["Emisor/RUTEmisor"]},
    {"nombre": "Factura electrónica (Costa Rica)", "raices": ("FacturaElectronica",), "beneficiario": ["Emisor/Nombre"],
     "numero": ["NumeroConsecutivo"], "monto": ["ResumenFactura/TotalComprobante"],
     "moneda": ["ResumenFactura/CodigoTipoMoneda/CodigoMoneda"], "moneda_defecto": "CRC", "vence": [],
     "id": ["Emisor/Identificacion/Numero"]},
    {"nombre": "SIFEN (Paraguay)", "raices": ("rDE", "DE"), "beneficiario": ["gEmis/dNomEmi"],
     "numero": ["gTimb/dEst+gTimb/dPunExp+gTimb/dNumDoc"], "monto": ["gTotSub/dTotGralOpe"], "moneda": ["gOpeCom/cMoneOpe"],
     "vence": ["gCuotas/dVencCuo"], "id": ["gEmis/dRucEm+gEmis/dDVEmi"]},
]
MONEDAS_NOMBRE = {"DOLAR": "USD"}                                   # EA12.4: SRI de Ecuador


def formato_de(raiz_nombre: str) -> dict | None:
    return next((f for f in FORMATOS if raiz_nombre in f["raices"]), None)


def decimal_xml(texto: str | None) -> Decimal | None:
    """EA12.3: en XML el decimal siempre es con punto; nada de separadores de miles."""
    if not texto or not re.fullmatch(r"\d+(\.\d+)?", texto.strip()):
        return None
    return Decimal(texto.strip())


def moneda_xml(valor: str | None, formato: dict) -> str | None:
    """EA12.4: el campo manda; solo si falta, la que fija el esquema."""
    if valor:
        v = MONEDAS_NOMBRE.get(valor.strip().upper(), valor.strip().upper())
        return v if len(v) == 3 and v.isalpha() else None
    return formato.get("moneda_defecto")


def _nombre(el) -> str:
    return el.tag.rsplit("}", 1)[-1]


def _hijo(el, *ruta):
    """Primer descendiente directo por nombre local, siguiendo la ruta."""
    for nombre in ruta:
        el = next((h for h in el if _nombre(h) == nombre), None)
        if el is None:
            return None
    return el


def _texto(el) -> str | None:
    return el.text.strip() if el is not None and el.text and el.text.strip() else None


def _desenvolver(texto_interno: str | None, que: str):
    if not texto_interno or "<" not in texto_interno:
        raise XmlInvalido(f"{que} no trae la factura.")
    crudo = texto_interno.encode("utf-8")
    if PELIGROSO.search(crudo):
        raise XmlInvalido("El XML declara entidades o DOCTYPE: no se acepta.")
    try:
        return ET.fromstring(crudo)
    except ET.ParseError as e:
        raise XmlInvalido(f"La factura dentro de {que.lower()} no es un XML válido.") from e


def analizar(datos: bytes):
    """Raíz de la factura, desenvolviendo el AttachedDocument de la DIAN y la autorizacion del SRI (EA10.1, EA12.8)."""
    if PELIGROSO.search(datos):
        raise XmlInvalido("El XML declara entidades o DOCTYPE: no se acepta.")
    try:
        raiz = ET.fromstring(datos)
    except ET.ParseError as e:
        raise XmlInvalido("El archivo no es un XML válido.") from e
    if _nombre(raiz) == "AttachedDocument":
        raiz = _desenvolver(_texto(_hijo(raiz, "Attachment", "ExternalReference", "Description")), "El documento adjunto")
    elif _nombre(raiz) == "autorizacion":
        raiz = _desenvolver(_texto(_hijo(raiz, "comprobante")), "La autorización")
    if _nombre(raiz) not in ("Invoice", "Comprobante") and formato_de(_nombre(raiz)) is None:
        raise FormatoDesconocido("No es un formato de factura electrónica reconocido.")
    return raiz


def _descendiente(el, nombre):
    return next((d for d in el.iter() if d is not el and _nombre(d) == nombre), None)


def _ruta(raiz, ruta: str) -> str | None:
    """Texto de una ruta de la tabla («A/B»: primer descendiente A y, dentro, el primer B). «+» une con «-»."""
    partes = []
    for trozo in ruta.split("+"):
        el = raiz
        for paso in trozo.split("/"):
            el = _descendiente(el, paso)
            if el is None:
                break
        if _texto(el):
            partes.append(_texto(el))
    return "-".join(partes) or None


def primera_ruta(raiz, rutas, resolver=_ruta) -> str | None:
    return next((v for v in (resolver(raiz, r) for r in rutas) if v), None)


def _leer_tabla(raiz, formato) -> dict:
    """EA12.2: los campos de un formato de la tabla, con el analizador."""
    vence = primera_ruta(raiz, formato["vence"])
    campos = {"beneficiario": primera_ruta(raiz, formato["beneficiario"]),
              "numero": primera_ruta(raiz, formato["numero"]),
              "monto": decimal_xml(primera_ruta(raiz, formato["monto"])),
              "moneda": moneda_xml(primera_ruta(raiz, formato["moneda"]), formato),
              "vence": vence if vence and re.fullmatch(r"\d{4}-\d{2}-\d{2}", vence) else None,
              "cuenta": None, "orden_compra": None}
    campos["dudosos"] = sorted(k for k in ("beneficiario", "numero", "monto", "moneda", "vence") if campos[k] is None)
    campos["id_tributaria"] = primera_ruta(raiz, formato["id"])
    campos["formato"] = formato["nombre"]
    return campos


def _leer_cfdi(c) -> dict:
    """CFDI 3.3 y 4.0 de México (EA11). Todo sale de atributos; no hay vencimiento (EA11.4)."""
    tipo = c.get("TipoDeComprobante")
    if tipo != "I":
        raise XmlInvalido(f"El comprobante es de tipo «{tipo or 'sin tipo'}», no una factura de ingreso: "
                          "una nota de crédito, un pago o una nómina no se pagan como factura.")
    emisor = _hijo(c, "Emisor")
    serie, folio = (c.get("Serie") or "").strip(), (c.get("Folio") or "").strip()
    monto = decimal_xml(c.get("Total"))                          # EA12.3
    moneda = (c.get("Moneda") or "").strip().upper()
    rfc = ((emisor.get("Rfc") if emisor is not None else None) or "").strip().upper() or None
    timbre = next((e for e in c.iter() if _nombre(e) == "TimbreFiscalDigital"), None)
    campos = {"beneficiario": ((emisor.get("Nombre") or "").strip() or None) if emisor is not None else None,
              "numero": (f"{serie}-{folio}" if serie and folio else folio) or None,
              "monto": monto, "moneda": moneda if len(moneda) == 3 and moneda.isalpha() and moneda != "XXX" else None,
              "vence": None, "cuenta": None, "orden_compra": None}
    campos["dudosos"] = sorted(k for k in ("beneficiario", "numero", "monto", "moneda", "vence") if campos[k] is None)
    campos["id_tributaria"] = rfc
    campos["nit_dv"] = ("correcto" if id_tributaria.rfc_valido(rfc) else "incorrecto") if rfc else "incorrecto"
    campos["cufe"] = "presente" if timbre is not None and (timbre.get("UUID") or "").strip() else "falta"   # EA11.7
    campos["formato"] = "CFDI (México)"
    return campos


def leer(datos: bytes) -> dict:
    """Los campos de la ficha más la identificación del emisor y las señales de validez local."""
    f = analizar(datos)
    if _nombre(f) == "Comprobante":
        return _leer_cfdi(f)
    if _nombre(f) != "Invoice":
        return _leer_tabla(f, formato_de(_nombre(f)))
    parte = _hijo(f, "AccountingSupplierParty", "Party")
    nombre = (_texto(_hijo(parte, "PartyLegalEntity", "RegistrationName")) if parte is not None else None) \
        or (_texto(_hijo(parte, "PartyTaxScheme", "RegistrationName")) if parte is not None else None)
    id_el = None
    if parte is not None:
        id_el = _hijo(parte, "PartyTaxScheme", "CompanyID")
        if id_el is None:                                        # un Element sin hijos es «falso»: comparar con None
            id_el = _hijo(parte, "PartyLegalEntity", "CompanyID")
        if id_el is None:                                        # SUNAT (Perú): el RUC va en PartyIdentification
            id_el = _hijo(parte, "PartyIdentification", "ID")
    base = re.sub(r"\D", "", _texto(id_el) or "")
    # En PartyIdentification (SUNAT) schemeID es el tipo de documento («6» = RUC), no un dígito de verificación.
    dv = (id_el.get("schemeID") if id_el is not None and _nombre(id_el) == "CompanyID" else None) or None
    es_nit = id_el is not None and (id_el.get("schemeName") == "31" or dv is not None) and base != ""

    total = _hijo(f, "LegalMonetaryTotal", "PayableAmount")
    monto = decimal_xml(_texto(total))                           # EA12.3
    moneda = (total.get("currencyID") if total is not None else None) or _texto(_hijo(f, "DocumentCurrencyCode"))
    vence = (_texto(_hijo(f, "DueDate")) or _texto(_hijo(f, "PaymentMeans", "PaymentDueDate"))
             or _texto(_hijo(f, "PaymentTerms", "PaymentDueDate")))
    perfil = _texto(_hijo(f, "ProfileID")) or ""
    dian = "DIAN" in perfil.upper()
    cufe = _texto(_hijo(f, "UUID"))

    cuenta = _texto(_hijo(f, "PaymentMeans", "PayeeFinancialAccount", "ID"))
    orden = _texto(_hijo(f, "OrderReference", "ID"))
    campos = {"beneficiario": nombre, "numero": _texto(_hijo(f, "ID")), "monto": monto,
              "moneda": moneda.upper() if moneda and len(moneda) == 3 and moneda.isalpha() else None,
              "vence": vence if vence and re.fullmatch(r"\d{4}-\d{2}-\d{2}", vence) else None,
              "cuenta": cuenta, "orden_compra": orden}
    campos["dudosos"] = sorted(k for k in ("beneficiario", "numero", "monto", "moneda", "vence") if campos[k] is None)

    # Señales locales (EA10.5, EA10.6): no son una consulta a la DIAN.
    campos["id_tributaria"] = f"{base}-{dv}" if es_nit and dv else (base or None)
    campos["nit_dv"] = ("correcto" if id_tributaria.dv_correcto(base, dv) else "incorrecto") if es_nit and dv else None
    campos["cufe"] = ("presente" if cufe else "falta") if dian else None
    campos["formato"] = "UBL 2.1 (DIAN)" if dian else "UBL 2.1"
    return campos
