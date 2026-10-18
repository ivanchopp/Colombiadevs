"""Segunda lectura sin IA: patrones de texto (EA3)."""
import re
from datetime import date
from decimal import Decimal, InvalidOperation

MONEDAS = "COP|USD|EUR|BRL|MXN|ARS|CLP|PEN|BOB|CRC|ZAR"
NUM = r"\d[\d.,]*"
RE_MONTO = [
    re.compile(rf"(?<![A-Za-z])(?:total|monto|valor|importe|amount)(?:\s+(?:a\s+pagar|neto|de\s+la\s+factura))?[^\n\dA-Za-z]{{0,30}}?(?P<m>{NUM})\s*(?P<c>{MONEDAS})\b", re.I),
    re.compile(rf"(?<![A-Za-z])(?:total|monto|valor|importe|amount)[^\n\dA-Z]{{0,30}}?(?P<c>{MONEDAS})\s*(?P<m>{NUM})", re.I),
]
# Factura electrónica colombiana (EA3.4 a EA3.6): «TOTAL:» con el valor en la línea siguiente, sin moneda al lado.
RE_TOTAL_SOLO = re.compile(rf"(?<![A-Za-z])total(?:\s+a\s+pagar|\s+factura)?[ \t]*:\s*\$?\s*(?P<m>{NUM})", re.I)
RE_CODIGO_MONEDA = re.compile(rf"\b({MONEDAS})\b")
RE_FECHA = re.compile(r"(?:vence|vencimiento|fecha de vencimiento|due(?: date)?)[^\n\d]{0,20}"
                      r"(?P<f>\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})", re.I)
RE_BENEF = re.compile(r"^\s*(?:proveedor|emisor|de|from|vendor)\s*[:\-]\s*(?P<b>[^\n<]{2,80})", re.I | re.M)
RE_RAZON = re.compile(r"raz[oó]n\s+social(?:\s*/\s*nombre)?\s*:\s*(?P<b>[^\n<]{2,80})", re.I)
RE_NUMERO_DOC = re.compile(r"n(?:ro|[uú]mero|[°º])?\.?\s*(?:de\s+)?(?:doc(?:umento)?\.?|factura)\s*[:\-]?\s*"
                           r"(?P<n>(?=[A-Z0-9\-]*\d)[A-Z0-9][A-Z0-9\-]{2,24})", re.I)
RE_NUMERO = re.compile(r"(?:factura|invoice)\s*(?:n[°ºo.]*|no\.?|#|num(?:ero)?)?\s*[:\-]?\s*(?P<n>(?=[A-Z0-9\-]*\d)[A-Z0-9][A-Z0-9\-]{2,24})", re.I)


# Orden de compra e identificación tributaria del emisor (OC3.2): solo si la factura los trae.
RE_OC = re.compile(r"(?:[oó]rden\s+de\s+compra|purchase\s+order|\bO\.?C\.?|\bPO)\s*(?:n[°ºo.]*|no\.?|#|num(?:ero)?)?\s*[:\-]?\s*"
                   r"(?P<oc>[A-Z][A-Z0-9]{0,3}[\- ]?\d[A-Z0-9\- ]{2,20}\d|\d{5,15})", re.I)
RE_ID_TRIB = re.compile(r"\b(?:NIT|RUC|RFC|identificaci[oó]n\s+tributaria)\s*[:\-]?\s*(?P<id>(?=[A-Z0-9\-]*\d)[A-Z0-9][A-Z0-9\-]{7,15})", re.I)


def parsear_monto(texto: str) -> Decimal | None:
    t = texto.strip().rstrip(".,")
    if not t or not re.fullmatch(NUM, t):
        return None
    if "." in t and "," in t:
        decimal = "." if t.rfind(".") > t.rfind(",") else ","
        t = t.replace("," if decimal == "." else ".", "").replace(decimal, ".")
    elif "." in t or "," in t:
        sep = "." if "." in t else ","
        partes = t.split(sep)
        if len(partes) > 2 or len(partes[-1]) == 3:
            t = "".join(partes)                       # separador de miles
        else:
            t = ".".join(partes)
    try:
        return Decimal(t)
    except InvalidOperation:
        return None


def parsear_fecha(texto: str) -> date | None:
    try:
        if "-" in texto:
            return date.fromisoformat(texto)
        d, m, a = (int(x) for x in texto.split("/"))
        return date(a, m, d)
    except ValueError:
        return None


def _alfanum(t) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(t).upper())


def normalizar(t: str) -> str:
    return " ".join(t.upper().split())


def leer(texto: str | None) -> dict:
    """Campos que los patrones encuentran. Lo que no encuentra queda en None."""
    r = {"beneficiario": None, "numero": None, "monto": None, "moneda": None, "vence": None,
         "orden_compra": None, "id_tributaria": None}
    if not texto:
        return r
    oc = RE_OC.search(texto)
    if oc:
        r["orden_compra"] = oc.group("oc").strip().upper()
    ident = RE_ID_TRIB.search(texto)
    if ident:
        r["id_tributaria"] = ident.group("id").upper()
    for patron in RE_MONTO:
        m = patron.search(texto)
        if m and parsear_monto(m.group("m")) is not None:
            r["monto"], r["moneda"] = parsear_monto(m.group("m")), m.group("c").upper()
            break
    if r["monto"] is None:
        totales = [parsear_monto(m.group("m")) for m in RE_TOTAL_SOLO.finditer(texto)]
        totales = [x for x in totales if x is not None]
        if totales:
            r["monto"] = totales[-1]                                     # EA3.5: el último «TOTAL:»
            codigos = set(RE_CODIGO_MONEDA.findall(texto.upper()))
            if len(codigos) == 1:                                        # EA3.6: nunca se supone una moneda
                r["moneda"] = codigos.pop()
    f = RE_FECHA.search(texto)
    if f:
        r["vence"] = parsear_fecha(f.group("f"))
    b = RE_BENEF.search(texto)
    if b:
        r["beneficiario"] = b.group("b").strip()
    if r["beneficiario"] is None:
        b = RE_RAZON.search(texto)                                       # EA3.4: la primera es el emisor
        if b:
            r["beneficiario"] = b.group("b").strip()
    n = RE_NUMERO_DOC.search(texto) or RE_NUMERO.search(texto)
    if n:
        r["numero"] = n.group("n").upper()
    return r


def comparar(ia: dict, texto: str | None) -> tuple[str, list[str]]:
    """(coincide | no_coincide | no_disponible, campos que difieren).

    «coincide» solo si la segunda lectura encontró los cuatro campos (EA3.2). Sin texto, o sin ningún campo
    comparable, la segunda lectura no está disponible (EA3.3) y el motor escala (R2.2)."""
    patrones = leer(texto)
    if not texto or all(patrones[c] is None for c in ("beneficiario", "monto", "moneda", "vence")):
        return "no_disponible", []
    difieren = []
    for campo in ("beneficiario", "monto", "moneda", "vence"):
        a, b = ia.get(campo), patrones[campo]
        if a is None or b is None:
            difieren.append(campo)
        elif campo == "beneficiario" and normalizar(str(a)) != normalizar(str(b)):
            difieren.append(campo)
        elif campo == "monto" and Decimal(str(a)) != b:
            difieren.append(campo)
        elif campo == "moneda" and str(a).upper() != b:
            difieren.append(campo)
        elif campo == "vence" and str(a) != str(b):
            difieren.append(campo)
    for campo in ("orden_compra", "id_tributaria"):                      # OC3.2: solo cuentan si alguien los vio
        a, b = ia.get(campo), patrones[campo]
        if (a is not None or b is not None) and (a is None or b is None or _alfanum(a) != _alfanum(b)):
            difieren.append(campo)
    return ("coincide" if not difieren else "no_coincide"), difieren
