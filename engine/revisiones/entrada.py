"""R2: la entrada es confiable o se escala."""
from decimal import Decimal, InvalidOperation

from ..modelos import Revision
from .comun import normalizar


def revisar(ficha, ctx, reglas):
    rs = [Revision(regla="R2.1", resultado="OK", mensaje="La ficha cumple el esquema.")]

    if ficha.segunda_lectura == "no_coincide":
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

    if ficha.orden_en_texto:
        rs.append(Revision(regla="R2.4", resultado="AVISO", efecto="ESCALAR", nivel="PERSONA",
                           observado="orden en el texto", umbral="ninguna",
                           mensaje="El texto de la factura traía una orden; se ignoró."))
    return rs
