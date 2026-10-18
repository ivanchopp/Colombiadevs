"""Arma el contexto del motor a partir del acta: historial, gasto y obligaciones usadas."""
from decimal import Decimal

from acta.estado import facturas_por_estado

from .compras import ocs_facturadas
from .modelos import Contexto, Movimiento


def contexto_desde_acta(base: Contexto, filas) -> Contexto:
    facturas = facturas_por_estado(filas)
    historial = list(base.historial)
    usadas: dict[str, str] = {}
    for f in facturas.values():
        d = f.decision
        if d.get("ficha_invalida"):
            continue                                  # sin monto ni fecha válidos: no cuenta (R8.6)
        historial.append(Movimiento(
            factura_id=f.factura_id, beneficiario=d["beneficiario"], numero=d["numero"],
            monto=Decimal(d["monto"]), moneda=d["moneda"], vence=d["vence"],
            monto_base=Decimal(d["monto_base"]), estado=f.estado, periodo=d["periodo"]))
        if d.get("obligacion_id"):
            usadas[d["obligacion_id"]] = f.factura_id
    calendario = [o.model_copy(update={"factura_id": usadas.get(o.id, o.factura_id)})
                  for o in base.calendario]
    return base.model_copy(update={"historial": historial, "calendario": calendario,
                                   "oc_facturadas": {**base.oc_facturadas, **ocs_facturadas(facturas.values())}})
