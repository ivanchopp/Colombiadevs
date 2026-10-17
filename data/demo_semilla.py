"""Facturas de ejemplo de las maquetas de «Ruta de una factura».

Cada ficha pasa por el motor de reglas y por el guardarraíl: ninguna decisión se escribe a mano.
Todo es ficticio (supuesto). El preparador `semilla-demo` marca lo que no subió el visitante.
"""
from datetime import date

PREPARADOR = "semilla-demo"


def _ficha(fid, benef, numero, monto, moneda, vence, recibida, cuenta, **extra):
    return dict(factura_id=fid, beneficiario=benef, numero=numero, monto=monto, moneda=moneda,
                vence=vence, recibida=recibida, cuenta_original=cuenta, lectura_ia="ok",
                segunda_lectura="coincide", preparador=PREPARADOR, **extra)


FICHAS = [
    _ficha("F-1042", "Pixel Norte Ltda.", "PN-1042", "2400000", "COP", "2026-10-22", "2026-10-02",
           "Bancolombia ···1180"),
    _ficha("F-1046", "Cloudwerk GmbH", "CW-1046", "540", "USD", "2026-10-28", "2026-10-15",
           "Deutsche ···7712"),
    _ficha("F-1044", "Taller Azteca", "TA-0931", "12500", "MXN", "2026-09-25", "2026-10-06",
           "BBVA ···3304"),
    _ficha("F-1043", "Estúdio Verde", "EV-1043", "3800", "BRL", "2026-10-27", "2026-10-14",
           "Itaú ···5521"),
    _ficha("F-1045", "Nuevo Proveedor SAS", "NP-1045", "9600000", "COP", "2026-10-30", "2026-10-16",
           "Banco Andino ···9034", cuenta_aclarada="Banco Lago ···4821"),
    _ficha("F-1047", "Diseños Alba", "DA-1047", "4100000", "COP", "2026-10-29", "2026-10-16",
           "Davivienda ···6403", orden_en_texto=True),
]


def cargar(almacen, sala_id, hoy: date | None = None):
    """Evalúa y registra cada ficha, en orden, con el contexto que va dejando el acta."""
    from engine.contexto import contexto_desde_acta
    from engine.guardarrail import registrar_decision
    from engine.reglas_io import cargar_contexto_base, cargar_reglas, hoy_bogota
    hoy = hoy or hoy_bogota()
    reglas, _ = cargar_reglas(hoy)
    base = cargar_contexto_base(hoy)
    for ficha in FICHAS:
        ctx = contexto_desde_acta(base, almacen.filas(sala_id))
        registrar_decision(almacen, sala_id, ficha, ctx, reglas)
