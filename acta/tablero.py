"""Cifras del tablero, calculadas con código y Decimal (AC6)."""
import csv
import io
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from .estado import facturas_por_estado
from .exportar_csv import exportar_facturas

PRESUPUESTO_PERIODO = Decimal("100000000")   # supuesto: 100 M COP


@dataclass
class Cifras:
    pagadas: int
    frenadas: int
    pendientes: int
    atrasadas: int
    gasto: Decimal
    porcentaje: Decimal
    presupuesto: Decimal
    actualizado: str


def cifras(filas_acta, atrasadas=0, presupuesto=PRESUPUESTO_PERIODO) -> Cifras:
    fs = facturas_por_estado(filas_acta).values()
    gasto = sum((f.monto_base for f in fs if f.estado == "PAGADA"), Decimal("0"))
    return Cifras(
        pagadas=sum(f.estado == "PAGADA" for f in fs),
        frenadas=sum(f.estado == "FRENADA" for f in fs),
        pendientes=sum(f.estado == "PENDIENTE" for f in fs),
        atrasadas=atrasadas, gasto=gasto,
        porcentaje=(gasto / presupuesto * 100).quantize(Decimal("0.1")),
        presupuesto=presupuesto,
        actualizado=datetime.now(timezone.utc).isoformat(timespec="seconds"))


def totales_del_csv(contenido: bytes) -> dict:
    lector = csv.DictReader(io.StringIO(contenido.decode("utf-8-sig")))
    t = {"PAGADA": 0, "FRENADA": 0, "PENDIENTE": 0, "gasto": Decimal("0")}
    for r in lector:
        if r["estado"] in t:
            t[r["estado"]] += 1
        if r["estado"] == "PAGADA":
            t["gasto"] += Decimal(r["monto_base"])
    return t


def comprobar_consistencia(filas_acta) -> bool:
    """El tablero y el CSV deben sumar lo mismo (AC6.3)."""
    c = cifras(filas_acta)
    t = totales_del_csv(exportar_facturas(filas_acta))
    return (c.pagadas, c.frenadas, c.pendientes, c.gasto) == (
        t["PAGADA"], t["FRENADA"], t["PENDIENTE"], t["gasto"])
