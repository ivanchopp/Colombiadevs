"""pagos_aprobados.csv: la instrucción de pago para Blinka, solo a partir del acta (spec archivo-de-salida).

El sistema no mueve dinero: este archivo lo ejecuta Blinka. Entra únicamente lo que el acta tiene como
PAGADA (AS1.1) y la cuenta de destino sale del registro, nunca de la factura ni del chat (AS2.4)."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

from .estado import facturas_por_estado
from .exportar_csv import _escribir
from .verificar import verificar_cadena

COLUMNAS = ["lote_id", "factura_id", "numero_factura", "beneficiario", "id_tributaria", "cuenta_destino",
            "monto", "moneda", "monto_base", "canal", "orden_compra", "tipo_aprobacion", "aprobado_por",
            "rol_aprobador", "aprobado_utc", "fila_acta", "huella_corta", "supuesto"]


class CadenaRota(Exception):
    """El acta no pasa la verificación: no se genera el archivo (AS3.2)."""


@dataclass
class ResumenPagos:
    lote_id: str
    instrucciones: int = 0
    totales: dict = field(default_factory=dict)             # moneda -> Decimal
    sin_cuenta: list = field(default_factory=list)          # facturas aprobadas sin cuenta registrada (AS2.4)


def lote_id(sala_id: str, ahora: datetime) -> str:
    return f"{sala_id}-{ahora:%Y%m%dT%H%M%SZ}"


def nombre_archivo(sala_id: str, ahora: datetime) -> str:
    return f"pagos_aprobados_{sala_id}_{ahora:%Y-%m-%d}.csv"


def exportar_pagos(filas_acta, registros, lote: str, delimitador=",") -> tuple[bytes, ResumenPagos]:
    """`registros`: beneficiario -> objeto con `.cuenta` (el registro de la empresa)."""
    resumen = ResumenPagos(lote)
    filas = []
    for f in sorted(facturas_por_estado(filas_acta).values(), key=lambda x: x.fila_decision):
        d = f.decision
        if f.estado != "PAGADA" or d.get("ficha_invalida"):                       # AS1.1, AS1.2
            continue
        registro = registros.get(d["beneficiario"])
        if registro is None or not registro.cuenta:                              # AS2.4: ante la duda, fuera
            resumen.sin_cuenta.append(f.factura_id)
            continue
        manual = f.respuesta is not None
        r = f.respuesta or {}
        ficha = d.get("ficha") or {}
        monto = Decimal(str(d["monto"]))
        filas.append([lote, f.factura_id, ficha.get("numero") or "", d["beneficiario"],
                      ficha.get("id_tributaria") or "", registro.cuenta, monto, d["moneda"], d["monto_base"],
                      (r.get("canal_elegido") if manual else d.get("canal_sugerido")) or "",
                      ficha.get("orden_compra") or "", "MANUAL" if manual else "AUTOMATICA",
                      f.aprobador if manual else "motor de reglas", r.get("rol", "") if manual else "",
                      f.resuelto_en if manual else f.creado_en, f.fila_acta, f.huella[:10],
                      "sí" if d.get("supuesto") else "no"])
        resumen.instrucciones += 1
        resumen.totales[d["moneda"]] = resumen.totales.get(d["moneda"], Decimal("0")) + monto
    return _escribir(COLUMNAS, filas, delimitador), resumen


def generar(almacen, sala_id, registros, ahora: datetime | None = None) -> tuple[bytes, ResumenPagos, str]:
    """Verifica la cadena (AS3.2) y devuelve (archivo, resumen, nombre). Lanza CadenaRota si falla."""
    v = verificar_cadena(almacen, sala_id)
    if not v.correcta:
        raise CadenaRota(f"La cadena del acta se rompe en la fila #{v.primera_fila_mala}: no se genera el archivo.")
    ahora = ahora or datetime.now(timezone.utc)
    datos, resumen = exportar_pagos(almacen.filas(sala_id), registros, lote_id(sala_id, ahora))
    return datos, resumen, nombre_archivo(sala_id, ahora)
