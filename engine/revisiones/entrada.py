"""R2: la entrada es confiable o se escala."""
from decimal import Decimal, InvalidOperation

from ..modelos import Revision
from . import NoEvaluable
from .comun import a_base, monto_base, normalizar

OBLIGATORIOS = ("beneficiario", "numero", "monto", "moneda", "vence")


def _coincide_con_registros(campo, ficha, ctx, reglas) -> bool:
    """¿El valor que viene solo de una aclaración coincide con los registros de la empresa? (R2.5)"""
    reg = ctx.registros.get(ficha.beneficiario)
    if campo == "beneficiario":
        return reg is not None
    if reg is None:
        return False
    if campo == "moneda":
        return reg.acuerdo_moneda is not None and reg.acuerdo_moneda == ficha.moneda
    if campo == "monto":
        try:
            base = monto_base(ficha, ctx)
            referencias = [o.monto_base for o in ctx.calendario if o.beneficiario == ficha.beneficiario]
            if reg.acuerdo_monto is not None:
                referencias.append(a_base(reg.acuerdo_monto, reg.acuerdo_moneda or reglas.moneda_base, ctx)[0])
        except NoEvaluable:
            return False
        return any(abs(base - r) <= r * reglas.tolerancia_ok for r in referencias)
    return False                                  # número y vencimiento: no hay registro con qué contrastarlos


def revisar(ficha, ctx, reglas):
    rs = [Revision(regla="R2.1", resultado="OK", mensaje="La ficha cumple el esquema.")]

    if ficha.segunda_lectura == "no_disponible":                             # R2.2
        rs.append(Revision(regla="R2.2", resultado="FALLA", efecto="ESCALAR", nivel="PERSONA",
                           observado="no_disponible", umbral="coincide",
                           mensaje="La segunda lectura de la factura no estuvo disponible."))
    elif ficha.segunda_lectura == "no_coincide":
        rs.append(Revision(regla="R2.2", resultado="FALLA", efecto="ESCALAR", nivel="PERSONA",
                           observado="no_coincide", umbral="coincide",
                           mensaje="Las dos lecturas de la factura no coinciden."))
    elif ficha.lectura_ia == "dudosa":
        rs.append(Revision(regla="R2.2", resultado="AVISO", efecto="ESCALAR", nivel="PERSONA",
                           observado="dudosa", umbral="ok", mensaje="La lectura de la factura quedó dudosa."))
    else:
        rs.append(Revision(regla="R2.2", resultado="OK", mensaje="Las dos lecturas coinciden."))

    dif = []
    a = ficha.valores_aclarados
    if "beneficiario" in a and normalizar(str(a["beneficiario"])) != normalizar(ficha.beneficiario):
        dif.append("beneficiario")
    if "monto" in a:
        try:
            if Decimal(str(a["monto"])) != ficha.monto:
                dif.append("monto")
        except InvalidOperation:
            dif.append("monto")
    if dif:
        rs.append(Revision(regla="R2.3", resultado="FALLA", efecto="ESCALAR", nivel="SENIOR",
                           observado=", ".join(dif), umbral="sin diferencias",
                           mensaje=f"Lo aclarado por chat cambia el {' y el '.join(dif)} de la factura."))
    else:
        rs.append(Revision(regla="R2.3", resultado="OK", mensaje="Lo aclarado no cambia monto ni beneficiario."))

    aclarados = [c for c in OBLIGATORIOS if ficha.origen_campos.get(c) == "aclarado"]     # R2.5
    sin_respaldo = [c for c in aclarados if not _coincide_con_registros(c, ficha, ctx, reglas)]
    if sin_respaldo:
        rs.append(Revision(regla="R2.5", resultado="AVISO", efecto="ESCALAR", nivel="PERSONA",
                           observado=", ".join(sin_respaldo), umbral="coincide con los registros",
                           mensaje="Hay datos que vienen solo de una aclaración del proveedor y no "
                                   f"coinciden con los registros ({', '.join(sin_respaldo)})."))
    else:
        rs.append(Revision(regla="R2.5", resultado="OK",
                           mensaje="Los datos aclarados coinciden con los registros." if aclarados
                           else "Ningún dato obligatorio viene solo de una aclaración."))

    if ficha.orden_en_texto:
        rs.append(Revision(regla="R2.4", resultado="AVISO", efecto="ESCALAR", nivel="PERSONA",
                           observado="orden en el texto", umbral="ninguna",
                           mensaje="El texto de la factura traía una orden; se ignoró."))
    return rs
