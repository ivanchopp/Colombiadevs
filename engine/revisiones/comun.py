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


def normalizar(texto: str) -> str:
    return " ".join(texto.upper().split())


def huella_factura(beneficiario, numero, monto, fecha) -> str:
    return "|".join([normalizar(beneficiario), normalizar(numero),
                     f"{Decimal(monto).quantize(DOS):.2f}", fecha.isoformat()])


def moneda_texto(valor: Decimal, moneda="COP") -> str:
    ent, _, dec = f"{valor:,.2f}".partition(".")
    ent = ent.replace(",", ".")
    return f"{ent} {moneda}" if dec == "00" else f"{ent},{dec} {moneda}"


def porcentaje(valor: Decimal) -> str:
    return f"{(valor * 100).quantize(Decimal('0.1'))} %".replace(".", ",")
