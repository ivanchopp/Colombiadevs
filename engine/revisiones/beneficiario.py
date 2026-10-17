"""R4: quien cobra por primera vez o cambia de cuenta va al senior."""
from ..modelos import Revision


def revisar(ficha, ctx, reglas):
    reg = ctx.registros.get(ficha.beneficiario)
    if reg is None:
        return [Revision(regla="R4.1", resultado="FALLA", efecto="ESCALAR", nivel="SENIOR",
                         observado="no registrado", umbral="lista permitida",
                         mensaje="El beneficiario no está en la lista permitida."),
                Revision(regla="R4.2", resultado="FALLA", efecto="ESCALAR", nivel="SENIOR",
                         observado="sin cuenta registrada", umbral="cuenta registrada",
                         mensaje="No hay una cuenta registrada para comparar.")]
    rs = [Revision(regla="R4.1", resultado="OK", mensaje="El beneficiario está en la lista permitida.")]
    cuenta = ficha.cuenta_aclarada or ficha.cuenta_original
    if cuenta is None:
        rs.append(Revision(regla="R4.2", resultado="FALLA", efecto="ESCALAR", nivel="SENIOR",
                           observado="sin cuenta", umbral=reg.cuenta,
                           mensaje="La factura no trae cuenta para verificar."))
    elif cuenta.strip() != reg.cuenta.strip():
        rs.append(Revision(regla="R4.2", resultado="FALLA", efecto="ESCALAR", nivel="SENIOR",
                           observado=cuenta, umbral=reg.cuenta,
                           mensaje="La cuenta es distinta a la registrada."))
    else:
        rs.append(Revision(regla="R4.2", resultado="OK", mensaje="La cuenta coincide con la registrada."))
    return rs
