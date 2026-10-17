"""facturas.csv y eventos.csv, solo a partir del acta (AC5)."""
import csv
import io
import json

from .estado import facturas_por_estado

COLUMNAS = ["factura_id", "beneficiario", "monto_original", "moneda", "monto_base", "tasa", "estado",
            "decision_motor", "nivel", "aprobador", "rol_aprobador", "motivo", "reglas_fallidas",
            "canal_sugerido", "canal_elegido", "version_reglas", "fila_acta", "huella_corta",
            "creado_utc", "resuelto_utc", "supuesto"]


def seguro(celda):
    """Neutraliza fórmulas de hoja de cálculo (AC5.5)."""
    if isinstance(celda, str) and celda[:1] in ("=", "+", "-", "@"):
        return "'" + celda
    return celda


def _escribir(columnas, filas, delimitador=",") -> bytes:
    buf = io.StringIO(newline="")
    w = csv.writer(buf, delimiter=delimitador, lineterminator="\n")
    w.writerow(columnas)
    for fila in filas:
        w.writerow([seguro(x) for x in fila])
    return buf.getvalue().encode("utf-8-sig")


def exportar_facturas(filas_acta, delimitador=",") -> bytes:
    filas = []
    for f in sorted(facturas_por_estado(filas_acta).values(), key=lambda x: x.fila_decision):
        d, r = f.decision, f.respuesta or {}
        fallidas = ";".join(x["regla"] for x in d.get("revisiones", []) if x["resultado"] == "FALLA")
        filas.append([f.factura_id, d["beneficiario"], d["monto"], d["moneda"], d["monto_base"],
                      d.get("tasa", ""), f.estado, d["decision"], d["nivel"], f.aprobador or "",
                      r.get("rol", ""), d["motivo"], fallidas, d.get("canal_sugerido") or "",
                      r.get("canal_elegido") or "", d["version_reglas"], f.fila_acta, f.huella[:10],
                      f.creado_en, f.resuelto_en or "", "sí" if d.get("supuesto") else "no"])
    return _escribir(COLUMNAS, filas, delimitador)


def exportar_eventos(filas_acta, delimitador=",") -> bytes:
    cols = ["fila_acta", "tipo", "factura_id", "actor", "creado_utc", "huella_corta", "detalle"]
    filas = [[f.num, f.tipo, f.factura_id or "", f.actor, f.creado_en, f.huella[:10],
              json.dumps(f.payload, sort_keys=True, ensure_ascii=False)] for f in filas_acta]
    return _escribir(cols, filas, delimitador)
