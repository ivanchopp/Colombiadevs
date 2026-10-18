"""PP8: página de reglas. Cambios por sala, afloja/restringe, techo duro, vista previa y acta."""
from datetime import date
from decimal import Decimal

import pytest
from streamlit.testing.v1 import AppTest

from acta import salas
from acta.estado import facturas_por_estado
from app import apoyo
from engine.contexto import contexto_desde_acta
from engine.evaluar import evaluar
from engine.reglas_io import (ErrorDeReglas, cambios_que_aflojan, cargar_contexto_base, cargar_reglas,
                              reglas_de_sala, validar_cambio)
from engine.simular import simular
from tests.test_motor import ficha
from tests.test_paneles import RAIZ

HOY = date(2026, 10, 17)


@pytest.fixture
def base():
    return cargar_reglas(HOY)[0]


def cambios(almacen, sala):
    return [f for f in almacen.filas(sala) if f.tipo == "CAMBIO_REGLA"]


def test_pp8_5_valida_coherencia_y_techo(base):
    assert validar_cambio(base, {"autopago_max": Decimal("500")}).autopago_max == Decimal("500")
    for malo in ({"autopago_max": Decimal("3000")},                      # supera a persona_max
                 {"tolerancia_ok": Decimal("0.2")},                          # mayor que la de frenar
                 {"tolerancia_frenar": Decimal("1.5")},
                 {"presupuesto_periodo": Decimal("0")},
                 {"persona_max": Decimal("15000")},                       # supera el techo duro
                 {"limite_periodo_beneficiario": Decimal("12500.01")}):
        with pytest.raises(ErrorDeReglas):
            validar_cambio(base, malo)


def test_r9_4_detecta_lo_que_afloja(base):
    nuevas = validar_cambio(base, {"autopago_max": Decimal("1000"), "presupuesto_periodo": Decimal("22500")})
    assert cambios_que_aflojan(base, nuevas) == ["autopago_max"]


def test_pp8_4_la_persona_no_afloja_y_queda_el_intento(almacen, sala, base):
    with pytest.raises(ErrorDeReglas, match="senior"):
        apoyo.cambiar_reglas(almacen, sala, base, {"autopago_max": Decimal("1000")}, "PERSONA", "subir")
    assert not cambios(almacen, sala)
    intento = [f for f in almacen.filas(sala) if f.tipo == "INTENTO_RECHAZADO"][-1]
    assert intento.payload["intento"] == "CAMBIO_REGLA" and intento.payload["aflojan"] == ["autopago_max"]


def test_pp8_4_la_persona_restringe_y_el_senior_afloja(almacen, sala, base):
    apoyo.cambiar_reglas(almacen, sala, base, {"autopago_max": Decimal("500")}, "PERSONA", "más control")
    actuales = reglas_de_sala(base, almacen.filas(sala))
    fila = apoyo.cambiar_reglas(almacen, sala, actuales, {"autopago_max": Decimal("1000")}, "SENIOR", "volumen")
    p = fila.payload
    assert p["afloja"] and p["firmado_por"] == "Senior de finanzas" and p["version_anterior"] == "v12.s1"
    assert reglas_de_sala(base, almacen.filas(sala)).version == "v12.s2"


def test_pp8_6_motivo_obligatorio_y_sin_cambios(almacen, sala, base):
    with pytest.raises(ErrorDeReglas, match="motivo"):
        apoyo.cambiar_reglas(almacen, sala, base, {"autopago_max": Decimal("500")}, "SENIOR", "  ")
    with pytest.raises(ErrorDeReglas, match="No hay cambios"):
        apoyo.cambiar_reglas(almacen, sala, base, {}, "SENIOR", "nada")
    assert not cambios(almacen, sala)


def test_pp8_6_el_acta_guarda_antes_despues_y_quien(almacen, sala, base):
    fila = apoyo.cambiar_reglas(almacen, sala, base, {"tolerancia_frenar": Decimal("0.08")}, "PERSONA", "ajuste")
    p = fila.payload
    assert (p["antes"]["tolerancia_frenar"], p["despues"]["tolerancia_frenar"]) == ("0.10", "0.08")
    assert not p["afloja"] and p["firmado_por"] is None and p["pedido_por"] == "Persona de finanzas"
    assert facturas_por_estado(almacen.filas(sala)).keys()      # el cambio no rompe el estado de las facturas


def test_pp8_7_aplica_hacia_adelante_y_solo_en_la_sala(almacen, sala, base):
    otra = salas.crear(almacen)
    apoyo.cambiar_reglas(almacen, sala, base, {"autopago_max": Decimal("500")}, "PERSONA", "más control")
    filas = almacen.filas(sala)
    ctx = contexto_desde_acta(cargar_contexto_base(HOY), filas)
    nueva = evaluar(ficha(factura_id="T9", numero="PN-T9"), ctx, reglas_de_sala(base, filas))
    assert (nueva.decision, nueva.version_reglas) == ("ESCALAR", "v12.s1")
    assert facturas_por_estado(filas)["F-1042"].estado == "PAGADA"               # lo ya decidido no cambia
    assert reglas_de_sala(base, almacen.filas(otra)) == base                     # la otra sala no cambia


def test_r9_6_vista_previa_sin_escribir(almacen, sala, base):
    filas = almacen.filas(sala)
    ctx = contexto_desde_acta(cargar_contexto_base(HOY), filas)
    cambian = simular(filas, ctx, base, validar_cambio(base, {"autopago_max": Decimal("500")}))
    assert {c["factura_id"] for c in cambian} == {"F-1042", "F-1046"}
    assert all(c["despues"].startswith("ESCALAR") for c in cambian)
    assert len(almacen.filas(sala)) == len(filas)


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    monkeypatch.setenv("ACTA_DB", str(tmp_path / "app.db"))
    monkeypatch.setenv("FECHA_DEMO", HOY.isoformat())


def test_pp8_1_pagina_pide_rol_y_luego_muestra_reglas(entorno):
    at = AppTest.from_file(str(RAIZ / "app/pages/5_Reglas.py"), default_timeout=30)
    at.run()
    assert not at.exception and any("Elige un rol" in i.value for i in at.info)
    at = AppTest.from_file(str(RAIZ / "app/pages/5_Reglas.py"), default_timeout=30)
    at.session_state["rol"] = "PERSONA"                                        # rol elegido antes de entrar
    at.run()
    assert not at.exception
    assert any("Techo duro" in i.value for i in at.info)
    at.number_input(key="regla_autopago_max").set_value(1_000).run()           # aflojar (autopago de 750 a 1.000 USD)
    assert any("afloja" in w.value for w in at.warning)
    at.text_area(key="motivo_reglas").set_value("subir").run()
    at.button[0].click().run()
    assert any("senior" in e.value for e in at.error)
