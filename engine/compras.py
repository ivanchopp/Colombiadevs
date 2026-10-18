"""Proveedores y órdenes de compra: carga, validación y estado (spec ordenes-de-compra, OC1, OC2, OC5)."""
import logging
import re
from decimal import Decimal
from pathlib import Path

import yaml
from pydantic import ValidationError

from .modelos import OrdenCompra, Proveedor

DATA = Path(__file__).resolve().parent.parent / "data"
log = logging.getLogger(__name__)


class ErrorDeCompras(Exception):
    pass


def normalizar_oc(numero: str) -> str:
    """«po 2026 001», «PO-2026-001» y «PO2026001» son la misma orden."""
    return re.sub(r"[^A-Z0-9]", "", str(numero).upper())


def validar_ordenes(ordenes: list[OrdenCompra], proveedores: list[Proveedor]) -> dict[str, OrdenCompra]:
    """OC2.2: rechaza número repetido, proveedor inexistente o cuentas que no cuadran. OC2.3: marca ids distintas."""
    por_id = {p.id: p for p in proveedores}
    res: dict[str, OrdenCompra] = {}
    for oc in ordenes:
        clave = normalizar_oc(oc.numero)
        if clave in res:
            raise ErrorDeCompras(f"Orden repetida: {oc.numero}.")
        prov = por_id.get(oc.proveedor_id)
        if prov is None:
            raise ErrorDeCompras(f"{oc.numero}: el proveedor {oc.proveedor_id} no existe.")
        if oc.cantidad * oc.precio_unitario != oc.subtotal:
            raise ErrorDeCompras(f"{oc.numero}: cantidad × precio no da el subtotal.")
        if oc.subtotal + oc.iva != oc.total:
            raise ErrorDeCompras(f"{oc.numero}: subtotal + IVA no da el total.")
        marcas = [] if oc.id_tributaria == prov.id_tributaria else ["no_coincide_con_proveedor"]
        res[clave] = oc.model_copy(update={"marcas": marcas})
    return res


def cargar_proveedores(carpeta=None) -> list[Proveedor]:
    datos = yaml.safe_load((Path(carpeta or DATA) / "proveedores.yaml").read_text(encoding="utf-8"))
    return [Proveedor.model_validate(p) for p in datos["proveedores"]]


def cargar_ordenes(proveedores: list[Proveedor], carpeta=None) -> dict[str, OrdenCompra]:
    datos = yaml.safe_load((Path(carpeta or DATA) / "ordenes_compra.yaml").read_text(encoding="utf-8"))
    return validar_ordenes([OrdenCompra.model_validate(o) for o in datos["ordenes"]], proveedores)


def cargar_compras(carpeta=None) -> tuple[list[Proveedor], dict[str, OrdenCompra]]:
    """Falla seguro (OC1.5): si un archivo no sirve, queda vacío y toda OC citada será «inexistente» (senior)."""
    try:
        proveedores = cargar_proveedores(carpeta)
    except (ValidationError, KeyError, TypeError, OSError, yaml.YAMLError) as e:
        log.error("proveedores.yaml inválido; sin proveedores: %s", e)
        return [], {}
    try:
        return proveedores, cargar_ordenes(proveedores, carpeta)
    except (ValidationError, ErrorDeCompras, KeyError, TypeError, ArithmeticError, OSError, yaml.YAMLError) as e:
        log.error("ordenes_compra.yaml inválido; sin órdenes: %s", e)
        return proveedores, {}


def proveedor_por_nombre(ctx, nombre: str):
    return next((p for p in ctx.proveedores if p.nombre == nombre), None)


def proveedor_por_id(ctx, id_: int):
    return next((p for p in ctx.proveedores if p.id == id_), None)


def ocs_facturadas(facturas) -> dict[str, str]:
    """OC5.2: facturada si la usa una factura PAGADA o PENDIENTE; FRENADA y RECHAZADA la dejan abierta."""
    usadas: dict[str, str] = {}
    for f in facturas:
        oc = (f.decision.get("ficha") or {}).get("orden_compra")
        if oc and f.estado in ("PAGADA", "PENDIENTE") and not f.decision.get("ficha_invalida"):
            usadas.setdefault(normalizar_oc(oc), f.factura_id)
    return usadas


__all__ = ["normalizar_oc", "cargar_compras", "proveedor_por_nombre",
           "proveedor_por_id", "ocs_facturadas", "ErrorDeCompras", "Decimal"]
