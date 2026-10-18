"""Dígito de verificación del NIT colombiano, calculado en local (EA10.5, EA10.7).

Esto NO consulta a la DIAN: un dígito correcto no prueba que el NIT exista ni que la factura sea válida (EA10.8)."""
import re

PESOS = (3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71)
RE_NIT = re.compile(r"\bNIT\b[\s:.#\-]*(?P<n>\d{1,3}(?:[. ]\d{3}){1,4}|\d{5,15})\s*[-–]\s*(?P<d>\d)(?!\d)", re.I)


def digito_verificacion(base: str) -> int:
    """Módulo 11 con los pesos de la DIAN, de derecha a izquierda."""
    digitos = re.sub(r"\D", "", base)
    if not digitos or len(digitos) > len(PESOS):
        raise ValueError("NIT fuera de rango")
    resto = sum(int(d) * PESOS[i] for i, d in enumerate(reversed(digitos))) % 11
    return resto if resto < 2 else 11 - resto


def dv_correcto(base: str, dv: str) -> bool:
    try:
        return str(digito_verificacion(base)) == str(dv).strip()
    except ValueError:
        return False


def primer_nit(texto: str | None):
    """(nit sin puntos, dígito, correcto) del primer NIT con dígito en el texto, o None."""
    if not texto:
        return None
    m = RE_NIT.search(texto)
    if not m:
        return None
    base = re.sub(r"\D", "", m.group("n"))
    return base, m.group("d"), dv_correcto(base, m.group("d"))


# ---------------------------------------------------------------- RFC de México (EA11.6)
RE_RFC = re.compile(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$")
GENERICOS = {"XAXX010101000", "XEXX010101000"}
_TABLA_RFC = {c: i for i, c in enumerate("0123456789ABCDEFGHIJKLMN&OPQRSTUVWXYZ Ñ")}


def digito_rfc(base: str) -> str:
    """Dígito verificador de un RFC (módulo 11): `base` son los 11 o 12 caracteres anteriores al último."""
    r = base.upper()
    if len(r) == 11:                                     # persona moral: se antepone un espacio
        r = " " + r
    suma = sum(_TABLA_RFC[c] * (13 - i) for i, c in enumerate(r[:12]))
    d = 11 - suma % 11
    return "0" if d == 11 else "A" if d == 10 else str(d)


def rfc_valido(rfc: str | None) -> bool:
    """Formato, dígito verificador y que no sea un RFC genérico. No consulta al SAT (EA11.9)."""
    r = (rfc or "").strip().upper()
    if r in GENERICOS or not RE_RFC.match(r):
        return False
    try:
        return digito_rfc(r[:-1]) == r[-1]
    except KeyError:
        return False
