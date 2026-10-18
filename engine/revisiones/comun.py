import re
import unicodedata
from decimal import ROUND_HALF_UP, Decimal

from . import NoEvaluable

DOS = Decimal("0.01")


def a_base(ficha_monto: Decimal, moneda: str, ctx) -> tuple[Decimal, Decimal]:
    """(monto en moneda base, tasa usada). Falta la tasa: no se puede evaluar (R5.1)."""
    tasa = ctx.tasas.get(moneda)
    if tasa is None:
        raise NoEvaluable(f"Sin tipo de cambio para {moneda}.", "SENIOR")
    return (ficha_monto * tasa).quantize(DOS, ROUND_HALF_UP), tasa


def monto_base(ficha, ctx) -> Decimal:
    return a_base(ficha.monto, ficha.moneda, ctx)[0]


def clave_nombre(texto: str) -> str:
    """Nombre sin mayúsculas, tildes, puntos ni comas y con un solo espacio entre palabras (R4.4)."""
    sin_tildes = "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))
    return " ".join(re.sub(r"[.,]", "", sin_tildes.casefold()).split())


def nombre_registrado(nombre: str, ctx) -> str | None:
    """El nombre del registro al que corresponde `nombre`, o None si no hay ninguno o hay más de uno (R4.4)."""
    if nombre in ctx.registros:
        return nombre
    clave = clave_nombre(nombre)
    if not clave:
        return None
    coinciden = [k for k in ctx.registros if clave_nombre(k) == clave]
    return coinciden[0] if len(coinciden) == 1 else None


def normalizar(texto: str) -> str:
    return " ".join(texto.upper().split())


def huella_factura(beneficiario, numero, monto, fecha) -> str:
    return "|".join([normalizar(beneficiario), normalizar(numero),
                     f"{Decimal(monto).quantize(DOS):.2f}", fecha.isoformat()])


def moneda_texto(valor: Decimal, moneda: str) -> str:
    ent, _, dec = f"{valor:,.2f}".partition(".")
    ent = ent.replace(",", ".")
    return f"{ent} {moneda}" if dec == "00" else f"{ent},{dec} {moneda}"


def en_base(valor: Decimal, reglas) -> str:
    """Un monto con la moneda base de las reglas (R5.6): nunca una moneda fija."""
    return moneda_texto(valor, reglas.moneda_base)


def porcentaje(valor: Decimal) -> str:
    return f"{(valor * 100).quantize(Decimal('0.1'))} %".replace(".", ",")
