"""R3: lo repetido o lo que no cuadra se frena."""
from decimal import Decimal

from ..modelos import Revision
from . import NoEvaluable, orden_compra
from .comun import a_base, huella_factura, moneda_texto, monto_base, porcentaje


def duplicado(ficha, ctx, reglas):
    h = huella_factura(ficha.beneficiario, ficha.numero, ficha.monto, ficha.vence)
    for m in ctx.historial:
        if m.factura_id != ficha.factura_id and huella_factura(
                m.beneficiario, m.numero, m.monto, m.vence) == h:
            return [Revision(regla="R3.1", resultado="FALLA", efecto="FRENAR", observado=m.factura_id,
                             umbral="sin repetidas", mensaje=f"Repetida: igual a la {m.factura_id}.")]
    return [Revision(regla="R3.1", resultado="OK", mensaje="No es una factura repetida.")]


def acuerdo(ficha, ctx, reglas):
    reg = ctx.registros.get(ficha.beneficiario)
    if (reg is None or reg.acuerdo_monto is None) and orden_compra.respalda_acuerdo(ficha, ctx, reglas):
        return [Revision(regla="R3.5", resultado="OK", observado="orden de compra",
                         mensaje="La orden de compra hace las veces de acuerdo.")]            # OC4.1
    if reg is None or reg.acuerdo_monto is None:
        return [Revision(regla="R3.5", resultado="AVISO", efecto="ESCALAR", nivel="PERSONA",
                         observado="sin acuerdo", umbral="acuerdo registrado",
                         mensaje="No hay un acuerdo registrado con este proveedor.")]
    base = monto_base(ficha, ctx)
    ref, _ = a_base(reg.acuerdo_monto, reg.acuerdo_moneda or reglas.moneda_base, ctx)
    exceso = (base - ref) / ref
    obs, umbral = porcentaje(exceso) + " sobre lo acordado", f"{porcentaje(reglas.tolerancia_ok)} / {porcentaje(reglas.tolerancia_frenar)}"
    if exceso <= reglas.tolerancia_ok:                                   # R3.2
        return [Revision(regla="R3.2", resultado="OK", observado=obs, umbral=umbral,
                         mensaje="El monto coincide con lo acordado.")]
    if exceso <= reglas.tolerancia_frenar:                               # R3.3
        return [Revision(regla="R3.3", resultado="AVISO", efecto="ESCALAR", nivel="PERSONA",
                         observado=obs, umbral=umbral,
                         mensaje=f"El monto supera en {porcentaje(exceso)} lo acordado.")]
    return [Revision(regla="R3.4", resultado="FALLA", efecto="FRENAR", observado=obs, umbral=umbral,
                     mensaje="No cuadra con lo acordado: lo supera en más de "
                             f"{porcentaje(reglas.tolerancia_frenar)}.")]


def gasto_periodo(ctx) -> Decimal:
    """Solo lo pagado o aprobado cuenta para el presupuesto (decisión D2)."""
    return sum((m.monto_base for m in ctx.historial
                if m.estado == "PAGADA" and m.periodo == ctx.periodo), Decimal("0"))


def presupuesto_y_techo(ficha, ctx, reglas):
    base = monto_base(ficha, ctx)
    rs = []
    total = gasto_periodo(ctx) + base
    if total > reglas.presupuesto_periodo:                               # R3.6
        rs.append(Revision(regla="R3.6", resultado="FALLA", efecto="FRENAR",
                           observado=moneda_texto(total), umbral=moneda_texto(reglas.presupuesto_periodo),
                           mensaje="Sin presupuesto: el gasto del periodo superaría el límite."))
    else:
        rs.append(Revision(regla="R3.6", resultado="OK", observado=moneda_texto(total),
                           umbral=moneda_texto(reglas.presupuesto_periodo),
                           mensaje="Cabe en el presupuesto del mes."))
    if base > reglas.techo_duro_pago:                                    # R3.7
        rs.append(Revision(regla="R3.7", resultado="FALLA", efecto="FRENAR", observado=moneda_texto(base),
                           umbral=moneda_texto(reglas.techo_duro_pago),
                           mensaje="Supera el techo duro de pago."))
    else:
        rs.append(Revision(regla="R3.7", resultado="OK", observado=moneda_texto(base),
                           umbral=moneda_texto(reglas.techo_duro_pago),
                           mensaje="No supera el techo duro."))
    return rs


__all__ = ["duplicado", "acuerdo", "presupuesto_y_techo", "gasto_periodo", "NoEvaluable"]
