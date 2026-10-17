"""Sugerencia de canal de pago (R7). Solo recomienda: nunca cambia la decisión ni envía nada."""
from decimal import Decimal

from .modelos import CanalEvaluado, CanalSugerido

COSTO = {"bajo": 0, "medio": 1, "alto": 2}


def sugerir_canal(ficha, ctx, reglas) -> CanalSugerido:
    reg = ctx.registros.get(ficha.beneficiario)
    pais = reg.pais if reg else None
    horas_hasta_vencer = Decimal((ficha.vence - ctx.hoy).days * 24)
    viables, otros = [], []
    for c in ctx.canales:
        if ficha.moneda not in c.monedas:
            otros.append(CanalEvaluado(nombre=c.nombre, etiqueta="No sugerido", costo=c.costo or "sin dato",
                                       tiempo_horas=c.tiempo_horas, supuesto=c.supuesto,
                                       razon=f"No: no paga en {ficha.moneda}."))
        elif "*" not in c.paises and pais not in c.paises:
            otros.append(CanalEvaluado(nombre=c.nombre, etiqueta="No sugerido", costo=c.costo or "sin dato",
                                       tiempo_horas=c.tiempo_horas, supuesto=c.supuesto,
                                       razon="No: no cubre el país del beneficiario."))
        else:
            viables.append(c)
    # Primero los que llegan a tiempo, luego costo y tiempo; «sin dato» va al final.
    def clave(c):
        tarde = c.tiempo_horas is not None and c.tiempo_horas > horas_hasta_vencer
        return (tarde, COSTO.get(c.costo, 9), c.tiempo_horas if c.tiempo_horas is not None else Decimal(10**6))
    evaluados, sugerido = [], None
    for c in sorted(viables, key=clave):
        if c.requiere_verificacion:
            etiqueta, razon = "Revisar", "Solo en parte: falta verificar la billetera o el dato del beneficiario."
        elif sugerido is None:
            etiqueta, razon, sugerido = "Sugerido", "Sí: cubre la moneda y el país del beneficiario.", c.nombre
        else:
            etiqueta, razon = "Alternativa", "Posible: también cubre la moneda y el país."
        evaluados.append(CanalEvaluado(nombre=c.nombre, etiqueta=etiqueta, razon=razon,
                                       costo=c.costo or "sin dato", tiempo_horas=c.tiempo_horas,
                                       supuesto=c.supuesto))
    aviso = None
    if not viables:
        aviso = "Sin canal compatible: avisar a la persona de finanzas."
    elif sugerido is None:
        aviso = "Ningún canal está listo: hay que verificar el dato del beneficiario."
    return CanalSugerido(sugerido=sugerido, evaluados=evaluados + otros, aviso=aviso)
