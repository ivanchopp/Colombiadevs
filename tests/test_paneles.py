from datetime import date
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from acta.estado import facturas_por_estado
from app import apoyo
from app.apoyo import AprobacionRechazada
from engine.contexto import contexto_desde_acta
from engine.reglas_io import cargar_contexto_base, cargar_reglas


def facturas(almacen, sala):
    return facturas_por_estado(almacen.filas(sala))


def test_pp5_1_cola_por_rol(almacen, sala):
    fs = facturas(almacen, sala)
    assert {f.factura_id for f in apoyo.cola_para_rol(fs, "PERSONA")} == {"F-1043", "F-1047"}
    assert {f.factura_id for f in apoyo.cola_para_rol(fs, "SENIOR")} == {"F-1043", "F-1045", "F-1047"}


def test_pp5_2_motivo_obligatorio(almacen, sala):
    f = facturas(almacen, sala)["F-1043"]
    for motivo in ("", "   ", "x" * 501):
        with pytest.raises(AprobacionRechazada):
            apoyo.responder(almacen, sala, f, "PERSONA", True, motivo, "Bre-B")
    assert facturas(almacen, sala)["F-1043"].estado == "PENDIENTE"


def test_pp5_3_rol_insuficiente_queda_en_el_acta(almacen, sala):
    f = facturas(almacen, sala)["F-1045"]              # nivel senior
    with pytest.raises(AprobacionRechazada):
        apoyo.responder(almacen, sala, f, "PERSONA", True, "motivo", "Bre-B")
    fs = facturas(almacen, sala)
    assert fs["F-1045"].estado == "PENDIENTE" and len(fs["F-1045"].intentos) == 1


def test_pp5_4_el_preparador_no_aprueba(almacen, sala, monkeypatch):
    f = facturas(almacen, sala)["F-1043"]
    monkeypatch.setitem(apoyo.ROLES, "PERSONA", f.decision["preparador"])   # el preparador intenta aprobar
    with pytest.raises(AprobacionRechazada):
        apoyo.responder(almacen, sala, f, "PERSONA", True, "motivo", "Bre-B")
    assert facturas(almacen, sala)["F-1043"].estado == "PENDIENTE"


def test_pp5_5_aprobar_registra_canal_y_pasa_a_pagada(almacen, sala):
    f = facturas(almacen, sala)["F-1047"]
    apoyo.responder(almacen, sala, f, "PERSONA", True, "Verificado con el contrato", "Bre-B")
    nuevo = facturas(almacen, sala)["F-1047"]
    assert nuevo.estado == "PAGADA" and nuevo.respuesta["canal_elegido"] == "Bre-B"


def test_rechazar_pasa_a_rechazada(almacen, sala):
    f = facturas(almacen, sala)["F-1045"]
    apoyo.responder(almacen, sala, f, "SENIOR", False, "Cuenta distinta")
    assert facturas(almacen, sala)["F-1045"].estado == "RECHAZADA"


def test_no_se_aprueba_dos_veces(almacen, sala):
    f = facturas(almacen, sala)["F-1047"]
    apoyo.responder(almacen, sala, f, "PERSONA", True, "ok", "Bre-B")
    with pytest.raises(AprobacionRechazada):
        apoyo.responder(almacen, sala, f, "PERSONA", True, "otra vez", "Bre-B")


def test_formato_monto():
    assert apoyo.formato_monto("9600000", "COP") == "9.600.000 COP"
    assert apoyo.formato_monto("12500.50", "MXN") == "12.500,50 MXN"


def test_pp6_2_estados_del_calendario(almacen, sala):
    hoy = date(2026, 10, 17)
    ctx = contexto_desde_acta(cargar_contexto_base(hoy), almacen.filas(sala))
    est = {(e["proveedor"], e["fecha"].day): e["estado"]
           for e in apoyo.estados_calendario(ctx, cargar_reglas(hoy)[0])}
    assert est[("Imprenta Sol", 14)] == "atrasada"
    assert est[("Hosting Andes", 21)] == "pendiente"
    assert est[("Pixel Norte Ltda.", 2)] == "llegó"


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    monkeypatch.setenv("ACTA_DB", str(tmp_path / "app.db"))


RAIZ = Path(__file__).resolve().parent.parent


def abrir(ruta):
    at = AppTest.from_file(str(RAIZ / ruta), default_timeout=30)
    at.run()
    return at


def test_pp1_1_panel_1_crea_sala_y_no_muestra_reglas(entorno):
    at = abrir("app/Panel_1_Proveedor.py")
    assert not at.exception
    sala = at.query_params["sala"][0]
    texto = " ".join(x.value for x in at.text) + " ".join(x.value for x in at.info)
    assert sala and "Has usado 0 de 5" in texto
    for prohibido in ("3.000.000", "Beneficiario nuevo y cuenta", "umbral", "SENIOR"):
        assert prohibido not in texto


@pytest.mark.parametrize("pagina", ["Tablero", "Cola_de_aprobacion", "Calendario", "Acta"])
def test_pp3_1_panel_2_pide_rol_antes_de_mostrar_datos(entorno, pagina):
    ruta = {"Tablero": "1_Tablero", "Cola_de_aprobacion": "2_Cola_de_aprobacion",
            "Calendario": "3_Calendario", "Acta": "4_Acta"}[pagina]
    at = abrir(f"app/pages/{ruta}.py")
    assert not at.exception
    assert any("Elige un rol" in i.value for i in at.info)
    assert len(at.dataframe) == 0
