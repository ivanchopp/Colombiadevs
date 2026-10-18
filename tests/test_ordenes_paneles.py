"""Spec paneles-y-despliegue PP9 (OC6, OT7): la página de órdenes de compra y la orden en el detalle."""
from datetime import date
from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from acta.estado import facturas_por_estado
from agents import ejemplos, flujo
from app import apoyo
from engine.contexto import contexto_desde_acta
from engine.reglas_io import cargar_contexto_base
from tests.test_agente_entrada import ClienteFalso, sin_clave  # noqa: F401 (fixture autouse)

RAIZ = Path(__file__).resolve().parent.parent
HOY = date(2026, 10, 17)


@pytest.fixture(autouse=True)
def fecha(monkeypatch):
    monkeypatch.setenv("FECHA_DEMO", HOY.isoformat())
    monkeypatch.setenv("FACTURAS_MAX", "20")


def subir(almacen, sala, clave):
    nombre, datos = ejemplos.leer_ejemplo(clave)
    return flujo.recibir(almacen, sala, nombre, datos, cliente=ClienteFalso(ejemplos.LECTURAS_GUARDADAS[clave]))


def vista(almacen, sala):
    filas = almacen.filas(sala)
    ctx = contexto_desde_acta(cargar_contexto_base(HOY), filas)
    return ctx, facturas_por_estado(filas)


# --- PP9.1: la tabla ---------------------------------------------------------------------------
def test_pp9_1_sin_facturas_todas_las_ordenes_estan_abiertas(almacen, sala):
    ctx, facturas = vista(almacen, sala)
    ordenes = apoyo.ordenes_con_estado(ctx, facturas)
    assert len(ordenes) == 7 and {o["estado"] for o in ordenes} == {"abierta"}
    primera = ordenes[0]
    assert primera["numero"] == "PO-2026-001" and primera["proveedor"] == "Agroindustrias del Huila S.A.S."
    assert primera["total"] == "1.160.000 COP" and primera["factura"] == "—"


def test_pp9_1_una_orden_pagada_queda_facturada_con_la_factura_que_la_uso(almacen, sala):
    subir(almacen, sala, "oc_cuadra")
    ctx, facturas = vista(almacen, sala)
    fila = next(o for o in apoyo.ordenes_con_estado(ctx, facturas) if o["numero"] == "PO-2026-001")
    assert fila["estado"] == "facturada" and fila["estado_factura"] == "pagada"
    assert fila["factura"] in facturas


def test_pp9_1_una_factura_frenada_deja_la_orden_abierta(almacen, sala):
    subir(almacen, sala, "oc_monto")
    ctx, facturas = vista(almacen, sala)
    fila = next(o for o in apoyo.ordenes_con_estado(ctx, facturas) if o["numero"] == "PO-2026-010")
    assert fila["estado"] == "abierta"


def test_pp9_1_una_factura_escalada_consume_la_orden(almacen, sala):
    subir(almacen, sala, "oc_nit")
    ctx, facturas = vista(almacen, sala)
    fila = next(o for o in apoyo.ordenes_con_estado(ctx, facturas) if o["numero"] == "PO-2026-005")
    assert fila["estado"] == "facturada" and fila["estado_factura"] == "escalada"


def test_pp9_2_la_orden_con_identificacion_distinta_se_ve_con_su_advertencia(almacen, sala):
    ctx, facturas = vista(almacen, sala)
    fila = next(o for o in apoyo.ordenes_con_estado(ctx, facturas) if o["numero"] == "PO-2026-021")
    assert "no coincide" in fila["advertencia"]
    assert all(o["advertencia"] == "—" for o in apoyo.ordenes_con_estado(ctx, facturas) if o["numero"] != "PO-2026-021")


def test_pp9_5_sin_ordenes_cargadas_la_lista_queda_vacia(almacen, sala):
    ctx, facturas = vista(almacen, sala)
    assert apoyo.ordenes_con_estado(ctx.model_copy(update={"ordenes": {}}), facturas) == []


# --- PP9.3: el detalle de la factura -----------------------------------------------------------
def test_pp9_3_la_factura_que_cita_una_orden_la_muestra_con_el_resultado_de_oc4(almacen, sala):
    e = subir(almacen, sala, "oc_cuadra")
    ctx, facturas = vista(almacen, sala)
    oc = apoyo.oc_de_factura(facturas[e["factura_id"]], ctx)
    assert oc["existe"] and oc["numero"] == "PO-2026-001" and oc["total"] == "1.160.000 COP"
    assert oc["proveedor"] == "Agroindustrias del Huila S.A.S." and "OK" in oc["resultado"]


def test_pp9_3_una_orden_que_no_existe_se_dice_y_no_se_inventa(almacen, sala):
    lectura = {**ejemplos.LECTURAS_GUARDADAS["oc_cuadra"], "orden_compra": "PO-2026-999"}
    nombre, datos = ejemplos.leer_ejemplo("oc_cuadra")
    datos = datos.replace(b"PO-2026-001", b"PO-2026-999")
    e = flujo.recibir(almacen, sala, nombre, datos, cliente=ClienteFalso(lectura))
    ctx, facturas = vista(almacen, sala)
    oc = apoyo.oc_de_factura(facturas[e["factura_id"]], ctx)
    assert oc == {"numero": "PO-2026-999", "existe": False, "resultado": oc["resultado"]}
    assert "inexistente" in oc["resultado"]


def test_pp9_3_una_factura_sin_orden_no_muestra_nada(almacen, sala):
    ctx, facturas = vista(almacen, sala)
    assert apoyo.oc_de_factura(facturas["F-1042"], ctx) is None


# --- Las páginas -------------------------------------------------------------------------------
def abrir(pagina, monkeypatch, almacen, sala, rol="SENIOR"):
    st.cache_resource.clear()
    monkeypatch.setenv("ACTA_DB", almacen.ruta)
    at = AppTest.from_file(str(RAIZ / pagina), default_timeout=30)
    at.query_params["sala"] = sala
    if rol:
        at.session_state["rol"] = rol
    at.run()
    return at


def test_pp9_1_la_pagina_entra_como_persona_y_muestra_las_ordenes(monkeypatch, almacen, sala):
    sin_rol = abrir("app/pages/6_Ordenes_de_compra.py", monkeypatch, almacen, sala, rol=None)
    assert not sin_rol.exception and not any("Elige un rol" in i.value for i in sin_rol.info)      # PP3.1
    assert sin_rol.session_state["rol"] == "PERSONA"
    subir(almacen, sala, "oc_cuadra")
    at = abrir("app/pages/6_Ordenes_de_compra.py", monkeypatch, almacen, sala)
    assert not at.exception and len(at.dataframe) == 1
    tabla = at.dataframe[0].value
    assert len(tabla) == 7 and set(tabla["Estado"]) == {"abierta", "facturada"}
    assert {m.label: m.value for m in at.metric} == {"Órdenes": "7", "Abiertas": "6", "Facturadas": "1"}
    assert any("ejemplo" in c.value and "supuesto" in c.value for c in at.caption)


def test_pp9_3_el_detalle_del_tablero_muestra_la_orden_citada(monkeypatch, almacen, sala):
    e = subir(almacen, sala, "oc_cuadra")
    at = abrir("app/pages/1_Tablero.py", monkeypatch, almacen, sala)
    assert not at.exception
    at.selectbox(key="detalle").set_value(e["factura_id"]).run()
    texto = " ".join(t.value for t in at.text)
    assert "Orden de compra PO-2026-001" in texto and "Agroindustrias del Huila" in texto
    assert "Revisión de la orden:" in texto


def test_pp9_4_el_panel_1_no_muestra_ordenes(monkeypatch, almacen, sala):
    subir(almacen, sala, "oc_cuadra")
    at = abrir("app/Envía_facturas.py", monkeypatch, almacen, sala, rol=None)
    assert not at.exception
    visible = " ".join(x.value for x in [*at.text, *at.info, *at.caption, *at.markdown, *at.success, *at.warning])
    for prohibido in ("PO-2026", "Orden de compra", "orden de compra", "inexistente", "ya facturada", "autorizad"):
        assert prohibido not in visible
