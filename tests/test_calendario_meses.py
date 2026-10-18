"""PP6.4: el calendario se puede ver mes a mes, también los meses futuros."""
from datetime import date, timedelta
from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from app.apoyo import meses_del_calendario, semanas_del_mes

RAIZ = Path(__file__).resolve().parent.parent


def abrir(monkeypatch, almacen, sala):
    st.cache_resource.clear()
    monkeypatch.setenv("ACTA_DB", almacen.ruta)
    monkeypatch.setenv("FECHA_DEMO", "2026-10-17")
    at = AppTest.from_file(str(RAIZ / "app/pages/3_Calendario.py"), default_timeout=30)
    at.query_params["sala"] = sala
    at.run()
    return at


def boton(at, texto):
    return next(b for b in at.button if texto in b.label)


def test_pp6_4_los_meses_van_del_primero_con_datos_a_doce_meses_despues():
    ev = [{"fecha": date(2026, 10, 2)}, {"fecha": date(2026, 10, 30)}]
    m = meses_del_calendario(ev, date(2026, 10, 17))
    assert len(m) == 13 and m[0] == (2026, 10) and m[-1] == (2027, 10) and (2026, 12) in m and (2027, 1) in m
    assert meses_del_calendario(ev, date(2026, 8, 1))[0] == (2026, 8)          # un «hoy» anterior amplía el rango


@pytest.mark.parametrize("anio,mes", [(2026, 10), (2026, 11), (2026, 12), (2027, 1), (2027, 2), (2028, 2)])
def test_pp6_4_la_cuadricula_cubre_todos_los_dias_habiles_del_mes(anio, mes):
    semanas = semanas_del_mes(anio, mes)
    dias = [d for s in semanas for d in s]
    habiles = [date(anio, mes, 1) + timedelta(days=k) for k in range(31)]
    habiles = [d for d in habiles if d.month == mes and d.weekday() < 5]
    assert all(h in dias for h in habiles) and all(len(s) == 5 for s in semanas)
    assert all(s[0].weekday() == 0 for s in semanas) and len(semanas) <= 6          # termina, también en diciembre


def test_pp6_4_abre_en_el_mes_de_las_obligaciones_y_las_muestra(monkeypatch, almacen, sala):
    at = abrir(monkeypatch, almacen, sala)
    assert not at.exception and at.session_state["mes_calendario"] == (2026, 10)
    assert any("Octubre 2026" in s.value for s in at.subheader)
    assert not any("No hay obligaciones esperadas" in i.value for i in at.info)
    assert any("Tecnología Cafetera" in t.value for t in at.text)               # las obligaciones del mes están


def test_pp6_4_noviembre_y_diciembre_traen_obligaciones_de_ejemplo_pendientes(monkeypatch, almacen, sala):
    at = abrir(monkeypatch, almacen, sala)
    boton(at, "Siguiente").click().run()
    assert not at.exception and at.session_state["mes_calendario"] == (2026, 11)
    assert any("Noviembre 2026" in s.value for s in at.subheader)
    assert not any("No hay obligaciones esperadas" in i.value for i in at.info)
    texto = " ".join(t.value for t in at.text)
    assert "Tecnología Cafetera" in texto and "… pendiente" in texto and "! atrasada" not in texto   # hoy es 17 oct
    boton(at, "Siguiente").click().run()
    assert at.session_state["mes_calendario"] == (2026, 12) and any("Diciembre 2026" in s.value for s in at.subheader)
    assert "Tecnología Cafetera" in " ".join(t.value for t in at.text)


def test_pp6_4_un_mes_sin_datos_lo_dice_y_no_inventa_obligaciones(monkeypatch, almacen, sala):
    at = abrir(monkeypatch, almacen, sala)
    at.selectbox(key="mes_calendario").set_value((2027, 1)).run()
    assert not at.exception and any("Enero 2027" in s.value for s in at.subheader)
    assert any("No hay obligaciones esperadas este mes" in i.value for i in at.info)
    assert not any("Tecnología Cafetera" in t.value for t in at.text)
    boton(at, "Anterior").click().run()
    assert at.session_state["mes_calendario"] == (2026, 12)


def test_pp6_4_las_obligaciones_de_ejemplo_son_dias_habiles_y_de_proveedores_validos():
    from engine.reglas_io import cargar_contexto_base
    ctx = cargar_contexto_base(date(2026, 10, 17))
    assert all(o.fecha.weekday() < 5 for o in ctx.calendario)                    # el calendario solo dibuja lunes a viernes
    assert {(o.fecha.year, o.fecha.month) for o in ctx.calendario} == {(2026, 10), (2026, 11), (2026, 12)}
    assert len({o.id for o in ctx.calendario}) == len(ctx.calendario)


def test_pp6_4_no_se_sale_del_rango(monkeypatch, almacen, sala):
    at = abrir(monkeypatch, almacen, sala)
    assert boton(at, "Anterior").disabled and not boton(at, "Siguiente").disabled
    at.selectbox(key="mes_calendario").set_value((2027, 10)).run()
    assert not at.exception and boton(at, "Siguiente").disabled and not boton(at, "Anterior").disabled
    assert len(at.selectbox(key="mes_calendario").options) == 13


def test_pp6_4_volver_a_octubre_muestra_otra_vez_las_obligaciones(monkeypatch, almacen, sala):
    at = abrir(monkeypatch, almacen, sala)
    boton(at, "Siguiente").click().run()
    boton(at, "Anterior").click().run()
    assert any("Tecnología Cafetera" in t.value for t in at.text)
