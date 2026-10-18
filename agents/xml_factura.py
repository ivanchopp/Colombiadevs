"""Lectura estructural de la factura electrónica UBL 2.1 (DIAN y otros países), sin IA (EA10).

La segunda lectura del XML es otro método, por patrones de texto (`segunda_lectura.leer_xml`)."""
import re
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation

from . import id_tributaria

PELIGROSO = re.compile(rb"<!\s*(DOCTYPE|ENTITY)", re.I)


class XmlInvalido(Exception):
    pass


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


def analizar(datos: bytes):
    """Árbol de la factura (Invoice), desenvolviendo el AttachedDocument de la DIAN (EA10.1, EA10.3)."""
    if PELIGROSO.search(datos):
        raise XmlInvalido("El XML declara entidades o DOCTYPE: no se acepta.")
    try:
        raiz = ET.fromstring(datos)
    except ET.ParseError as e:
        raise XmlInvalido("El archivo no es un XML válido.") from e
    if _nombre(raiz) == "AttachedDocument":
        interno = _texto(_hijo(raiz, "Attachment", "ExternalReference", "Description"))
        if not interno or "<" not in interno:
            raise XmlInvalido("El documento adjunto no trae la factura.")
        crudo = interno.encode("utf-8")
        if PELIGROSO.search(crudo):
            raise XmlInvalido("El XML declara entidades o DOCTYPE: no se acepta.")
        try:
            raiz = ET.fromstring(crudo)
        except ET.ParseError as e:
            raise XmlInvalido("La factura dentro del documento adjunto no es un XML válido.") from e
    if _nombre(raiz) != "Invoice":
        raise XmlInvalido("No es una factura UBL (Invoice).")
    return raiz


def leer(datos: bytes) -> dict:
    """Los campos de la ficha más la identificación del emisor y las señales de validez local."""
    f = analizar(datos)
    parte = _hijo(f, "AccountingSupplierParty", "Party")
    nombre = (_texto(_hijo(parte, "PartyLegalEntity", "RegistrationName")) if parte is not None else None) \
        or (_texto(_hijo(parte, "PartyTaxScheme", "RegistrationName")) if parte is not None else None)
    id_el = None
    if parte is not None:
        id_el = _hijo(parte, "PartyTaxScheme", "CompanyID")
        if id_el is None:                                        # un Element sin hijos es «falso»: comparar con None
            id_el = _hijo(parte, "PartyLegalEntity", "CompanyID")
    base = re.sub(r"\D", "", _texto(id_el) or "")
    dv = (id_el.get("schemeID") if id_el is not None else None) or None
    es_nit = id_el is not None and (id_el.get("schemeName") == "31" or dv is not None) and base != ""

    total = _hijo(f, "LegalMonetaryTotal", "PayableAmount")
    try:
        monto = Decimal(_texto(total)) if _texto(total) else None
    except InvalidOperation:
        monto = None
    moneda = (total.get("currencyID") if total is not None else None) or _texto(_hijo(f, "DocumentCurrencyCode"))
    vence = _texto(_hijo(f, "DueDate")) or _texto(_hijo(f, "PaymentMeans", "PaymentDueDate"))
    perfil = _texto(_hijo(f, "ProfileID")) or ""
    dian = "DIAN" in perfil.upper()
    cufe = _texto(_hijo(f, "UUID"))

    cuenta = _texto(_hijo(f, "PaymentMeans", "PayeeFinancialAccount", "ID"))
    campos = {"beneficiario": nombre, "numero": _texto(_hijo(f, "ID")), "monto": monto,
              "moneda": moneda.upper() if moneda and len(moneda) == 3 and moneda.isalpha() else None,
              "vence": vence if vence and re.fullmatch(r"\d{4}-\d{2}-\d{2}", vence) else None,
              "cuenta": cuenta}
    campos["dudosos"] = sorted(k for k in ("beneficiario", "numero", "monto", "moneda", "vence") if campos[k] is None)

    # Señales locales (EA10.5, EA10.6): no son una consulta a la DIAN.
    campos["id_tributaria"] = f"{base}-{dv}" if es_nit and dv else (base or None)
    campos["nit_dv"] = ("correcto" if id_tributaria.dv_correcto(base, dv) else "incorrecto") if es_nit and dv else None
    campos["cufe"] = ("presente" if cufe else "falta") if dian else None
    return campos
