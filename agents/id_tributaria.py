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
