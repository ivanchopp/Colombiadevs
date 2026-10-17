"""Archivo de salida de pagos aprobados (spec archivo-de-salida, AS1 a AS4). Sin red y sin clave."""
import csv
import io
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest

from acta import exportar_pagos
from acta.estado import facturas_por_estado
from app import apoyo
from engine.reglas_io import cargar_contexto_base, hoy_bogota

AHORA = datetime(2026, 10, 17, 22, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def registros():
    return cargar_contexto_base(hoy_bogota()).registros


def filas_csv(datos: bytes):
    return list(csv.DictReader(io.StringIO(datos.decode("utf-8-sig"))))


def generar(almacen, sala, registros):
    datos, resumen, nombre = exportar_pagos.generar(almacen, sala, registros, AHORA)
    return filas_csv(datos), resumen, nombre


def estados(almacen, sala):
    return {k: v.estado for k, v in facturas_por_estado(almacen.filas(sala)).items()}


def test_as1_1_solo_entran_las_pagadas(almacen, sala, registros):
    filas, resumen, _ = generar(almacen, sala, registros)
    pagadas = {k for k, e in estados(almacen, sala).items() if e == "PAGADA"}
    assert pagadas and {f["factura_id"] for f in filas} == pagadas
    assert resumen.instrucciones == len(pagadas)
    # La sala de ejemplo trae también facturas frenadas y pendientes: ninguna entra (AS1.2)
    assert {"FRENADA", "PENDIENTE"} <= set(estados(almacen, sala).values())


def test_as1_2_rechazada_y_pendiente_no_entran(almacen, sala, registros):
    f = facturas_por_estado(almacen.filas(sala))["F-1045"]
    apoyo.responder(almacen, sala, f, "SENIOR", False, "Cuenta distinta")
    ids = {x["factura_id"] for x in generar(almacen, sala, registros)[0]}
    assert "F-1045" not in ids and "F-1043" not in ids and "F-1044" not in ids


def test_as1_3_aprobacion_manual_lleva_canal_y_aprobador(almacen, sala, registros):
    f = facturas_por_estado(almacen.filas(sala))["F-1047"]
    apoyo.responder(almacen, sala, f, "PERSONA", True, "Verificado con el contrato", "Bre-B")
    filas = {x["factura_id"]: x for x in generar(almacen, sala, registros)[0]}
    manual, auto = filas["F-1047"], filas["F-1042"]
    assert manual["tipo_aprobacion"] == "MANUAL" and manual["canal"] == "Bre-B"
    assert manual["aprobado_por"] and manual["rol_aprobador"]
    assert auto["tipo_aprobacion"] == "AUTOMATICA" and auto["aprobado_por"] == "motor de reglas"
    assert auto["canal"]                                            # AS2.3: el sugerido por el motor


def test_as1_4_un_intento_rechazado_no_cambia_el_resultado(almacen, sala, registros):
    antes = {x["factura_id"] for x in generar(almacen, sala, registros)[0]}
    f = facturas_por_estado(almacen.filas(sala))["F-1045"]
    with pytest.raises(apoyo.AprobacionRechazada):
        apoyo.responder(almacen, sala, f, "PERSONA", True, "intento", "Bre-B")     # una persona no aprueba al senior
    assert {x["factura_id"] for x in generar(almacen, sala, registros)[0]} == antes


def test_as2_2_monto_y_moneda_son_los_de_la_factura(almacen, sala, registros):
    filas = {x["factura_id"]: x for x in generar(almacen, sala, registros)[0]}
    cw = filas["F-1046"]
    assert (cw["monto"], cw["moneda"]) == ("540.00", "USD") and Decimal(cw["monto_base"]) > Decimal("540")


def test_as2_4_la_cuenta_sale_del_registro(almacen, sala, registros):
    filas = {x["factura_id"]: x for x in generar(almacen, sala, registros)[0]}
    assert filas["F-1042"]["cuenta_destino"] == registros["Pixel Norte Ltda."].cuenta
    otro = {**registros, "Pixel Norte Ltda.": SimpleNamespace(cuenta="Banco Registro ···0001")}
    filas = {x["factura_id"]: x for x in generar(almacen, sala, otro)[0]}
    assert filas["F-1042"]["cuenta_destino"] == "Banco Registro ···0001"


def test_as2_4_sin_cuenta_registrada_queda_fuera_y_se_avisa(almacen, sala, registros):
    sin = {k: v for k, v in registros.items() if k != "Pixel Norte Ltda."}
    filas, resumen, _ = generar(almacen, sala, sin)
    assert "F-1042" not in {x["factura_id"] for x in filas} and resumen.sin_cuenta == ["F-1042"]


def test_as2_5_neutraliza_formulas(almacen, sala, registros):
    peligroso = {**registros, "Pixel Norte Ltda.": SimpleNamespace(cuenta='=HYPERLINK("http://x","y")')}
    filas = {x["factura_id"]: x for x in generar(almacen, sala, peligroso)[0]}
    assert filas["F-1042"]["cuenta_destino"].startswith("'=")


def test_as2_6_marca_supuesto(almacen, sala, registros):
    assert {x["supuesto"] for x in generar(almacen, sala, registros)[0]} <= {"sí", "no"}


def test_as3_2_cadena_rota_no_genera_archivo(almacen, sala, registros):
    filas = almacen.filas(sala)
    manipuladas = [replace(filas[0], payload={**filas[0].payload, "monto": "1"})] + filas[1:]
    falso = SimpleNamespace(filas=lambda _s: manipuladas)
    with pytest.raises(exportar_pagos.CadenaRota, match="no se genera"):
        exportar_pagos.generar(falso, sala, registros, AHORA)


def test_as3_4_sin_aprobadas_no_hay_instrucciones(registros):
    datos, resumen = exportar_pagos.exportar_pagos([], registros, "L")
    assert resumen.instrucciones == 0 and filas_csv(datos) == []


def test_as3_5_y_3_6_lote_y_nombre(almacen, sala, registros):
    filas, _, nombre = generar(almacen, sala, registros)
    assert {x["lote_id"] for x in filas} == {f"{sala}-20261017T220000Z"}
    assert nombre == f"pagos_aprobados_{sala}_2026-10-17.csv"


def test_as4_1_no_trae_motivos_ni_umbrales(almacen, sala, registros):
    datos = exportar_pagos.generar(almacen, sala, registros, AHORA)[0].decode("utf-8-sig").lower()
    for prohibido in ("motivo", "umbral", "límite", "limite", "r2.", "r3."):
        assert prohibido not in datos
    assert "motor de reglas" in datos                                # única mención: quién aprobó


def test_as4_2_una_ficha_invalida_nunca_entra(almacen, sala, registros):
    from agents import flujo
    e = flujo.recibir(almacen, sala, "vacia.txt", b"hola, adjunto mi factura")
    e = flujo.responder(almacen, sala, e["factura_id"], "no")
    e = flujo.responder(almacen, sala, e["factura_id"], "no")
    ids = {x["factura_id"] for x in generar(almacen, sala, registros)[0]}
    assert e["factura_id"] not in ids


def test_as4_2_defensa_extra_ficha_invalida_marcada_pagar_no_entra(almacen, sala, registros):
    """El guardarraíl ya lo impide; si un acta alterada lo trajera, el archivo tampoco la incluye."""
    filas = almacen.filas(sala)
    base = next(f for f in filas if f.tipo == "DECISION" and f.payload["decision"] == "PAGAR")
    rara = replace(base, factura_id="F-9999", payload={**base.payload, "factura_id": "F-9999", "ficha_invalida": True})
    datos, resumen = exportar_pagos.exportar_pagos(filas + [rara], registros, "L")
    assert "F-9999" not in {x["factura_id"] for x in filas_csv(datos)}


def test_as4_2_el_filtro_exige_el_estado_pagada(almacen, sala, registros, monkeypatch):
    """Mutación: si alguien dejara pasar otros estados, esta prueba lo detecta."""
    real = exportar_pagos.facturas_por_estado
    def todas_pagadas(filas):
        res = real(filas)
        for f in res.values():
            f.estado = "PAGADA"
        return res
    monkeypatch.setattr(exportar_pagos, "facturas_por_estado", todas_pagadas)
    assert len(generar(almacen, sala, registros)[0]) > len(
        [e for e in estados(almacen, sala).values() if e == "PAGADA"])


def test_as3_3_el_acta_muestra_el_aviso_y_el_resumen(monkeypatch, almacen, sala):
    import streamlit as st
    from pathlib import Path
    st.cache_resource.clear()                     # la conexión a la base se guarda en caché entre pruebas
    monkeypatch.setenv("ACTA_DB", almacen.ruta)
    ruta = Path(__file__).resolve().parent.parent / "app/pages/4_Acta.py"
    at = AppTest.from_file(str(ruta), default_timeout=30)
    at.query_params["sala"] = sala
    at.session_state["rol"] = "PERSONA"
    at.run()
    assert not at.exception
    texto = " ".join(m.value for m in at.markdown) + " ".join(c.value for c in at.caption)
    assert "no mueve dinero" in texto and "instrucciones de pago" in texto
