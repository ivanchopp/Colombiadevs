"""Siete facturas de ejemplo (tres citan una orden de compra) y lo que la IA leería de ellas. Solo para pruebas y evaluación (EA8.4)."""
from pathlib import Path

DIRECTORIO = Path(__file__).resolve().parent.parent / "data" / "facturas_ejemplo"

EJEMPLOS = {
    "normal": "Normal",
    "repetida": "Repetida",
    "beneficiario_nuevo": "Beneficiario nuevo",
    "orden_escondida": "Con orden escondida",
    "oc_cuadra": "Con orden de compra que cuadra",
    "oc_monto": "Con orden de compra y monto alterado",
    "oc_nit": "Con orden de compra e identificación distinta",
}

# Nombre neutro para descargar: solo el proveedor y la factura, sin decir qué caso es (PP2.5).
ROTULOS = {
    "normal": "Alimentos del Valle S.A.S. · IS-2210",
    "repetida": "Papelería Corporativa Anáhuac S.A. de C.V. · TA-0931",
    "beneficiario_nuevo": "Estudio Nube · EN-0077",
    "orden_escondida": "Consultores Energéticos Magdalena S.A.S. · HA-5531",
    "oc_cuadra": "Agroindustrias del Huila S.A.S. · AH-4410",
    "oc_monto": "Textiles Modernos Pereira S.A.S. · TM-2207",
    "oc_nit": "Consultores Energéticos Magdalena S.A.S. · CE-0932",
}

# Lo que devolvería la lectura con IA (supuesto), para correr la demo sin clave.
LECTURAS_GUARDADAS = {
    "normal": dict(beneficiario="Alimentos del Valle S.A.S.", numero="IS-2210", monto="1800000", moneda="COP",
                   vence="2026-10-30", cuenta="Cuenta demo ···0026", dudosos=[]),
    "repetida": dict(beneficiario="Papelería Corporativa Anáhuac S.A. de C.V.", numero="TA-0931", monto="12500", moneda="MXN",
                     vence="2026-09-25", cuenta="Cuenta demo ···0029", dudosos=[]),
    "beneficiario_nuevo": dict(beneficiario="Estudio Nube SAS", numero="EN-0077", monto="7200000", moneda="COP",
                               vence="2026-11-05", cuenta="Banco Lago ···4821", dudosos=[]),
    "orden_escondida": dict(beneficiario="Consultores Energéticos Magdalena S.A.S.", numero="HA-5531", monto="950000", moneda="COP",
                            vence="2026-11-05", cuenta="Cuenta demo ···0009", dudosos=[]),
    "oc_cuadra": dict(beneficiario="Agroindustrias del Huila S.A.S.", numero="AH-4410", monto="1160000", moneda="COP",
                      vence="2026-10-30", cuenta="Cuenta demo ···0004", orden_compra="PO-2026-001",
                      id_tributaria="999016272-1", dudosos=[]),
    "oc_monto": dict(beneficiario="Textiles Modernos Pereira S.A.S.", numero="TM-2207", monto="1334000", moneda="COP",
                     vence="2026-10-31", cuenta="Cuenta demo ···0010", orden_compra="PO-2026-010",
                     id_tributaria="978961183-0", dudosos=[]),
    "oc_nit": dict(beneficiario="Consultores Energéticos Magdalena S.A.S.", numero="CE-0932", monto="1160000", moneda="COP",
                   vence="2026-10-31", cuenta="Cuenta demo ···0009", orden_compra="PO-2026-005",
                   id_tributaria="929610444-9", dudosos=[]),
}


def leer_ejemplo(clave: str) -> tuple[str, bytes]:
    return f"{clave}.txt", (DIRECTORIO / f"{clave}.txt").read_bytes()
