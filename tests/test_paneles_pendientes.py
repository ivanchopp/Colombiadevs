"""PP2.7 y PP3.1 a PP3.5: Panel 1 «Envía facturas», rol inicial y punto rojo de pendientes."""
import json
from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from acta.estado import facturas_por_estado
from agents import flujo
from app import apoyo
from app.comun import _etiqueta_rol

RAIZ = Path(__file__).resolve().parent.parent


def abrir(pagina, monkeypatch, almacen, sala, rol=None):
    st.cache_resource.clear()
    monkeypatch.setenv("ACTA_DB", almacen.ruta)
    at = AppTest.from_file(str(RAIZ / pagina), default_timeout=30)
    at.query_params["sala"] = sala
    if rol:
        at.session_state["rol"] = rol
    at.run()
    return at


def pendientes_a_mano(almacen, sala):
    fs = facturas_por_estado(almacen.filas(sala)).values()
    return {n: sum(1 for f in fs if f.estado == "PENDIENTE" and f.decision["nivel"] == n
                   and not f.decision.get("ficha_invalida")) for n in ("PERSONA", "SENIOR")}


def test_pp2_7_el_panel_1_se_llama_envia_facturas(monkeypatch, almacen, sala):
    assert (RAIZ / "app" / "Envía_facturas.py").exists() and not (RAIZ / "app" / "Panel_1_Proveedor.py").exists()
    at = abrir("app/Envía_facturas.py", monkeypatch, almacen, sala)
    assert not at.exception and at.title[0].value == "Envía facturas"


def test_pp3_3_la_semilla_tiene_pendientes_y_el_conteo_coincide_con_el_acta(almacen, sala):
    cuenta = apoyo.pendientes_por_rol(facturas_por_estado(almacen.filas(sala)))
    assert cuenta == pendientes_a_mano(almacen, sala) and cuenta["PERSONA"] > 0 and cuenta["SENIOR"] > 0


def test_pp3_3_el_punto_rojo_lleva_el_numero_solo_si_hay_pendientes():
    assert _etiqueta_rol("PERSONA", {"PERSONA": 2, "SENIOR": 0}) == "Persona de finanzas 🔴 2"
    assert _etiqueta_rol("SENIOR", {"PERSONA": 2, "SENIOR": 0}) == "Senior de finanzas"
    assert _etiqueta_rol("SENIOR", {}) == "Senior de finanzas"


@pytest.mark.parametrize("pagina", ["1_Tablero", "2_Cola_de_aprobacion", "3_Calendario", "4_Acta", "5_Reglas",
                                    "6_Ordenes_de_compra"])
def test_pp3_3_el_selector_de_todas_las_paginas_muestra_el_punto_sobre_su_rol(monkeypatch, almacen, sala, pagina):
    esperado = pendientes_a_mano(almacen, sala)
    at = abrir(f"app/pages/{pagina}.py", monkeypatch, almacen, sala)
    assert not at.exception
    etiquetas = [o.content for o in at.segmented_control(key="selector_rol").proto.options]
    assert f"Persona de finanzas 🔴 {esperado['PERSONA']}" in etiquetas
    assert f"Senior de finanzas 🔴 {esperado['SENIOR']}" in etiquetas


def test_pp3_3_una_factura_sin_leer_no_cuenta_porque_solo_se_puede_rechazar(monkeypatch, almacen, sala):
    antes = pendientes_a_mano(almacen, sala)
    monkeypatch.setenv("FACTURAS_MAX", "20")
    from tests.test_agente_entrada import ClienteFalso
    flujo.recibir(almacen, sala, "f.txt", b"Hola, adjunto mi cuenta de cobro.", cliente=ClienteFalso({}, falla=True))
    for _ in range(3):                                  # el agente pregunta; el proveedor no sabe
        e = flujo.EstadoEntrada(almacen).obtener(sala, "F-2001") if hasattr(flujo, "EstadoEntrada") else None
        if e is None or e["estado"] != "recibida":
            break
        flujo.responder(almacen, sala, "F-2001", "no se")
    fs = facturas_por_estado(almacen.filas(sala))
    assert any(f.decision.get("ficha_invalida") for f in fs.values())        # existe y está pendiente de rechazo
    assert apoyo.pendientes_por_rol(fs) == antes == pendientes_a_mano(almacen, sala)


def test_pp3_4_el_menu_lateral_avisa_cuantas_pendientes_ve_el_rol(monkeypatch, almacen, sala):
    at = abrir("app/pages/2_Cola_de_aprobacion.py", monkeypatch, almacen, sala, rol="SENIOR")
    visibles = [f for f in apoyo.cola_para_rol(facturas_por_estado(almacen.filas(sala)), "SENIOR")
                if not f.decision.get("ficha_invalida")]
    texto = " ".join(m.value for m in at.sidebar.markdown)
    assert f"🔴 **{len(visibles)}** aprobación(es) pendiente(s)" in texto


def test_pp3_4_el_panel_1_nunca_muestra_pendientes(monkeypatch, almacen, sala):
    at = abrir("app/Envía_facturas.py", monkeypatch, almacen, sala)
    todo = " ".join(m.value for m in at.sidebar.markdown) + " ".join(m.value for m in at.markdown)
    assert "🔴" not in todo and "pendiente" not in todo.lower() and not at.segmented_control


def test_pp3_1_el_rol_elegido_se_recuerda_y_el_inicial_es_persona(monkeypatch, almacen, sala):
    assert abrir("app/pages/1_Tablero.py", monkeypatch, almacen, sala).session_state["rol"] == "PERSONA"
    at = abrir("app/pages/1_Tablero.py", monkeypatch, almacen, sala, rol="SENIOR")
    assert at.session_state["rol"] == "SENIOR" and at.segmented_control(key="selector_rol").value == "SENIOR"
