"""R6: calendario del mes."""
from datetime import timedelta

from ..modelos import Revision
from .comun import monto_base


def emparejar(ficha, ctx, reglas):
    """La obligación libre más cercana en fecha, o None (R6.1, R6.3)."""
    base = monto_base(ficha, ctx)
    candidatas = [o for o in ctx.calendario
                  if o.beneficiario == ficha.beneficiario
                  and o.factura_id in (None, ficha.factura_id)
                  and abs(base - o.monto_base) <= o.monto_base * reglas.tolerancia_ok
                  and abs((ficha.recibida - o.fecha).days) <= reglas.ventana_dias]
    return min(candidatas, key=lambda o: abs((ficha.recibida - o.fecha).days), default=None)


def revisar(ficha, ctx, reglas):
    o = emparejar(ficha, ctx, reglas)
    if o:
        return [Revision(regla="R6.1", resultado="OK", observado=o.id,
                         mensaje="Estaba en el calendario del mes.")]
    return [Revision(regla="R6.2", resultado="AVISO", efecto="ESCALAR", nivel="PERSONA",
                     observado="sin obligación", umbral="obligación esperada",
                     mensaje="No estaba en el calendario del mes (inesperada).")]


def estado_obligaciones(ctx, reglas):
    """«llegó», «pendiente» o «atrasada» (R6.4)."""
    salida = []
    for o in ctx.calendario:
        if o.factura_id:
            estado = "llegó"
        elif ctx.hoy > o.fecha + timedelta(days=reglas.dias_gracia):
            estado = "atrasada"
        else:
            estado = "pendiente"
        salida.append((o, estado))
    return salida
