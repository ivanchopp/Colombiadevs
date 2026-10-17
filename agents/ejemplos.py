"""Cuatro facturas de ejemplo y lo que la IA leería de ellas (modo demo, EA8.1)."""
from pathlib import Path

DIRECTORIO = Path(__file__).resolve().parent.parent / "data" / "facturas_ejemplo"

EJEMPLOS = {
    "normal": "Normal",
    "repetida": "Repetida",
    "beneficiario_nuevo": "Beneficiario nuevo",
    "orden_escondida": "Con orden escondida",
}

# Lo que devolvería la lectura con IA (supuesto), para correr la demo sin clave.
LECTURAS_GUARDADAS = {
    "normal": dict(beneficiario="Imprenta Sol", numero="IS-2210", monto="1800000", moneda="COP",
                   vence="2026-10-30", cuenta="Bancolombia ···2291", dudosos=[]),
    "repetida": dict(beneficiario="Taller Azteca", numero="TA-0931", monto="12500", moneda="MXN",
                     vence="2026-09-25", cuenta="BBVA ···3304", dudosos=[]),
    "beneficiario_nuevo": dict(beneficiario="Estudio Nube SAS", numero="EN-0077", monto="7200000", moneda="COP",
                               vence="2026-11-05", cuenta="Banco Lago ···4821", dudosos=[]),
    "orden_escondida": dict(beneficiario="Hosting Andes", numero="HA-5531", monto="950000", moneda="COP",
                            vence="2026-11-05", cuenta="Bancolombia ···7745", dudosos=[]),
}


def leer_ejemplo(clave: str) -> tuple[str, bytes]:
    return f"{clave}.txt", (DIRECTORIO / f"{clave}.txt").read_bytes()
