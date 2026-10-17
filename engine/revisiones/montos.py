"""R5: conversión, niveles por monto y límite por periodo."""
from decimal import Decimal

from ..modelos import Revision
from .comun import a_base, en_base, moneda_texto


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
    if ctx.tasas.get(reglas.moneda_base) != 1:                          # R5.7: la tabla debe estar en la base
        return [Revision(regla="R5.7", resultado="FALLA", efecto="ESCALAR", nivel="SENIOR",
                         observado=f"tasa de {reglas.moneda_base}: {ctx.tasas.get(reglas.moneda_base, 'sin dato')}",
                         umbral="1", mensaje="La tabla de cambio no coincide con la moneda base.")]
    base, tasa = a_base(ficha.monto, ficha.moneda, ctx)
    rs = [Revision(regla="R5.1", resultado="OK", observado=f"tasa {tasa}",
                   mensaje=f"Monto en {reglas.moneda_base}: {en_base(base, reglas)}.")]
    total = monto_para_nivel(ficha, ctx)
    nivel = nivel_por_monto(total, reglas)
    if nivel == "NINGUNO":
        rs.append(Revision(regla="R5.3", resultado="OK", observado=en_base(total, reglas),
                           umbral=en_base(reglas.autopago_max, reglas),
                           mensaje="El monto del periodo permite el pago automático."))
    else:
        rs.append(Revision(regla="R5.3", resultado="AVISO", efecto="ESCALAR", nivel=nivel,
                           observado=en_base(total, reglas), umbral=en_base(reglas.autopago_max, reglas),
                           mensaje=f"El monto del periodo ({en_base(total, reglas)}) supera el pago automático."))
    if total > reglas.limite_periodo_beneficiario:
        rs.append(Revision(regla="R5.4", resultado="FALLA", efecto="ESCALAR", nivel="SENIOR",
                           observado=en_base(total, reglas), umbral=en_base(reglas.limite_periodo_beneficiario, reglas),
                           mensaje="Supera el límite del periodo para este beneficiario."))
    else:
        rs.append(Revision(regla="R5.4", resultado="OK", observado=en_base(total, reglas),
                           umbral=en_base(reglas.limite_periodo_beneficiario, reglas),
                           mensaje="Dentro del límite del periodo para el beneficiario."))
    return rs
