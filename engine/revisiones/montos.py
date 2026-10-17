"""R5: conversión, niveles por monto y límite por periodo."""
from decimal import Decimal

from ..modelos import Revision
from .comun import a_base, moneda_texto


def monto_para_nivel(ficha, ctx) -> Decimal:
    """Pagado, aprobado o pendiente del beneficiario en el periodo, más esta factura (R5.2)."""
    previo = sum((m.monto_base for m in ctx.historial
                  if m.beneficiario == ficha.beneficiario and m.periodo == ctx.periodo
                  and m.factura_id != ficha.factura_id and m.estado in ("PAGADA", "PENDIENTE")),
                 Decimal("0"))
    return previo + a_base(ficha.monto, ficha.moneda, ctx)[0]


def nivel_por_monto(valor: Decimal, reglas) -> str:
    if valor <= reglas.autopago_max:
        return "NINGUNO"
    return "PERSONA" if valor <= reglas.persona_max else "SENIOR"


def revisar(ficha, ctx, reglas):
    base, tasa = a_base(ficha.monto, ficha.moneda, ctx)
    rs = [Revision(regla="R5.1", resultado="OK", observado=f"tasa {tasa}",
                   mensaje=f"Monto en {reglas.moneda_base}: {moneda_texto(base, reglas.moneda_base)}.")]
    total = monto_para_nivel(ficha, ctx)
    nivel = nivel_por_monto(total, reglas)
    if nivel == "NINGUNO":
        rs.append(Revision(regla="R5.3", resultado="OK", observado=moneda_texto(total),
                           umbral=moneda_texto(reglas.autopago_max),
                           mensaje="El monto del periodo permite el pago automático."))
    else:
        rs.append(Revision(regla="R5.3", resultado="AVISO", efecto="ESCALAR", nivel=nivel,
                           observado=moneda_texto(total), umbral=moneda_texto(reglas.autopago_max),
                           mensaje=f"El monto del periodo ({moneda_texto(total)}) supera el pago automático."))
    if total > reglas.limite_periodo_beneficiario:
        rs.append(Revision(regla="R5.4", resultado="FALLA", efecto="ESCALAR", nivel="SENIOR",
                           observado=moneda_texto(total), umbral=moneda_texto(reglas.limite_periodo_beneficiario),
                           mensaje="Supera el límite del periodo para este beneficiario."))
    else:
        rs.append(Revision(regla="R5.4", resultado="OK", observado=moneda_texto(total),
                           umbral=moneda_texto(reglas.limite_periodo_beneficiario),
                           mensaje="Dentro del límite del periodo para el beneficiario."))
    return rs
