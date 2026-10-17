"""Eventos de ejemplo tomados de las maquetas de «Ruta de una factura».

PROVISIONAL: mientras no exista el motor de reglas (engine/), estas decisiones se
escriben a mano para poder ver los paneles. Todo es ficticio y las tasas, canales y
fechas son «supuesto». Se sustituye por las decisiones reales del motor (tarea T15).
"""
from datetime import date
from decimal import Decimal

VERSION_REGLAS = "v12"
ORIGEN = "semilla_maqueta"

# Tasas de ejemplo a COP (supuesto).
TASAS = {"COP": "1", "USD": "4085", "BRL": "750", "MXN": "230"}


def _rev(regla, resultado, mensaje, efecto="NINGUNO"):
    return {"regla": regla, "resultado": resultado, "efecto": efecto, "mensaje": mensaje}


_OK_LECTURAS = _rev("R2.2", "OK", "Las dos lecturas coinciden.")
_OK_REPETIDA = _rev("R3.1", "OK", "No es una factura repetida.")
_OK_PRESUPUESTO = _rev("R3.6", "OK", "Cabe en el presupuesto del mes.")

# (factura, proveedor, país, monto, moneda, vence, decisión, nivel, motivo, canal, revisiones)
CASOS = [
    ("F-1042", "Pixel Norte Ltda.", "Colombia", "2400000", "COP", date(2026, 10, 22), "PAGAR", "NINGUNO",
     "Estaba en el calendario y cumple las reglas", "Bre-B",
     [_OK_LECTURAS, _OK_REPETIDA, _rev("R6.1", "OK", "Estaba en el calendario del mes."), _OK_PRESUPUESTO]),
    ("F-1046", "Cloudwerk GmbH", "Alemania", "540", "USD", date(2026, 10, 28), "PAGAR", "NINGUNO",
     "Estaba en el calendario y cumple las reglas", "Wire en USD",
     [_OK_LECTURAS, _OK_REPETIDA, _rev("R6.1", "OK", "Estaba en el calendario del mes."), _OK_PRESUPUESTO]),
    ("F-1044", "Taller Azteca", "México", "12500", "MXN", date(2026, 10, 25), "FRENAR", "NINGUNO",
     "Repetida: igual a la F-1031", None,
     [_OK_LECTURAS, _rev("R3.1", "FALLA", "Repetida: igual a la F-1031.", "FRENAR"), _OK_PRESUPUESTO]),
    ("F-1043", "Estúdio Verde", "Brasil", "3800", "BRL", date(2026, 10, 27), "ESCALAR", "PERSONA",
     "Monto 8% sobre lo acordado", None,
     [_OK_LECTURAS, _OK_REPETIDA,
      _rev("R3.3", "FALLA", "El monto supera en 8 % lo acordado (entre 5 % y 10 %).", "ESCALAR"),
      _OK_PRESUPUESTO]),
    ("F-1045", "Nuevo Proveedor SAS", "Colombia", "9600000", "COP", date(2026, 10, 30), "ESCALAR", "SENIOR",
     "Beneficiario nuevo y cuenta distinta", None,
     [_OK_LECTURAS,
      _rev("R4.1", "FALLA", "El beneficiario no está en la lista permitida.", "ESCALAR"),
      _rev("R4.2", "FALLA", "La cuenta aclarada es distinta a la registrada.", "ESCALAR"),
      _rev("R6.2", "AVISO", "No estaba en el calendario del mes."),
      _OK_REPETIDA, _OK_PRESUPUESTO]),
    ("F-1047", "Diseños Alba", "Colombia", "4100000", "COP", date(2026, 10, 29), "ESCALAR", "PERSONA",
     "No estaba en el calendario; el texto traía una orden que se ignoró", None,
     [_OK_LECTURAS, _rev("R6.2", "AVISO", "No estaba en el calendario del mes."),
      _rev("R2.4", "AVISO", "El texto de la factura traía una orden; se ignoró."),
      _OK_REPETIDA, _OK_PRESUPUESTO]),
]

# Calendario del mes (supuesto): (proveedor, fecha esperada, monto esperado COP, factura que lo cubre)
CALENDARIO = [
    ("Pixel Norte Ltda.", date(2026, 10, 2), "2400000", "F-1042"),
    ("Taller Azteca", date(2026, 10, 6), "2875000", "F-1044"),
    ("Imprenta Sol", date(2026, 10, 14), "1800000", None),
    ("Estúdio Verde", date(2026, 10, 14), "2850000", "F-1043"),
    ("Cloudwerk GmbH", date(2026, 10, 15), "2205900", "F-1046"),
    ("Hosting Andes", date(2026, 10, 21), "950000", None),
    ("Pixel Norte Ltda.", date(2026, 10, 28), "2400000", None),
    ("Contador externo", date(2026, 10, 30), "1500000", None),
]

PREPARADOR = "proveedor-demo"


def eventos_semilla():
    """Genera (tipo, factura_id, payload, actor) para cargar una sala nueva."""
    for fid, prov, pais, monto, mon, vence, dec, nivel, motivo, canal, revs in CASOS:
        tasa = TASAS[mon]
        base = f"{Decimal(monto) * Decimal(tasa):.2f}"
        yield ("DECISION", fid, {
            "factura_id": fid, "beneficiario": prov, "pais": pais, "monto": monto, "moneda": mon,
            "monto_base": base, "tasa": tasa, "decision": dec, "nivel": nivel, "revisiones": revs,
            "motivo": motivo, "version_reglas": VERSION_REGLAS, "canal_sugerido": canal,
            "preparador": PREPARADOR, "vence": vence.isoformat(), "supuesto": True, "origen": ORIGEN,
        }, "Motor de reglas")
