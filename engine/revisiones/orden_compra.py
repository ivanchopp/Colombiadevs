"""OC4: una factura que cita una orden de compra se compara con ella. Cualquier duda escala o frena."""
from ..compras import normalizar_oc, proveedor_por_id, proveedor_por_nombre
from ..modelos import Revision
from .comun import a_base, porcentaje


def _senior(regla, mensaje, observado="", umbral=""):
    return Revision(regla=regla, resultado="FALLA", efecto="ESCALAR", nivel="SENIOR",
                    observado=observado, umbral=umbral, mensaje=mensaje)


def _marcas_del_proveedor(ficha, ctx):
    prov = proveedor_por_nombre(ctx, ficha.beneficiario)
    return prov, (prov.marcas if prov else [])


def revisar(ficha, ctx, reglas):
    prov, marcas = _marcas_del_proveedor(ficha, ctx)
    if marcas:                                                           # OC4.4: aunque no cite OC
        return [_senior("OC4.4", "La identificación tributaria del proveedor está repetida o es inválida.",
                        ", ".join(marcas), "identificación única y válida")]
    if not ficha.orden_compra:                                           # OC4.8
        return [Revision(regla="OC4.8", resultado="OK", mensaje="No cita orden de compra.")]

    oc = ctx.ordenes.get(normalizar_oc(ficha.orden_compra))
    if oc is None:                                                       # OC4.2
        return [_senior("OC4.2", "Orden de compra inexistente.", ficha.orden_compra, "orden registrada")]
    dueno = proveedor_por_id(ctx, oc.proveedor_id)
    if (dueno is None or dueno.nombre != ficha.beneficiario or oc.marcas
            or (ficha.id_tributaria is not None and ficha.id_tributaria != oc.id_tributaria)):   # OC4.3, OC2.3
        return [_senior("OC4.3", "La identificación tributaria no coincide con la de la orden de compra.",
                        ficha.id_tributaria or "(sin identificación)", oc.id_tributaria)]
    if ficha.id_tributaria is None:                                      # el emisor no se pudo confirmar
        return [Revision(regla="OC4.3", resultado="AVISO", efecto="ESCALAR", nivel="PERSONA",
                         observado="sin identificación", umbral=oc.id_tributaria,
                         mensaje="La factura no trae identificación tributaria para confirmar al emisor.")]
    facturada_por = ctx.oc_facturadas.get(normalizar_oc(oc.numero))
    if facturada_por and facturada_por != ficha.factura_id:              # OC4.6
        return [Revision(regla="OC4.6", resultado="FALLA", efecto="FRENAR", observado=facturada_por,
                         umbral="orden abierta", mensaje=f"Orden de compra ya facturada por la {facturada_por}.")]

    base, _ = a_base(ficha.monto, ficha.moneda, ctx)                     # OC4.7
    ref, _ = a_base(oc.total, oc.moneda, ctx)
    exceso = (base - ref) / ref
    obs, umbral = porcentaje(exceso) + " sobre la orden", f"{porcentaje(reglas.tolerancia_ok)} / {porcentaje(reglas.tolerancia_frenar)}"
    if exceso <= reglas.tolerancia_ok:                                   # OC4.1
        return [Revision(regla="OC4.1", resultado="OK", observado=obs, umbral=umbral,
                         mensaje=f"Cuadra con la orden de compra {oc.numero}.")]
    if exceso <= reglas.tolerancia_frenar:                               # OC4.5
        return [Revision(regla="OC4.5", resultado="AVISO", efecto="ESCALAR", nivel="PERSONA",
                         observado=obs, umbral=umbral,
                         mensaje=f"El monto supera en {porcentaje(exceso)} la orden de compra.")]
    return [Revision(regla="OC4.5", resultado="FALLA", efecto="FRENAR", observado=obs, umbral=umbral,
                     mensaje="No cuadra con la orden de compra: la supera en más de "
                             f"{porcentaje(reglas.tolerancia_frenar)}.")]


def respalda_acuerdo(ficha, ctx, reglas) -> bool:
    """OC4.1: una OC que cuadra hace las veces de acuerdo. Solo si toda la revisión de la OC da OK."""
    if not ficha.orden_compra:
        return False
    rs = revisar(ficha, ctx, reglas)
    return bool(rs) and all(r.resultado == "OK" for r in rs) and rs[0].regla == "OC4.1"
