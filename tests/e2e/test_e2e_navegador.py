"""Extremo a extremo con un navegador real: el recorrido completo del proveedor y de finanzas.

Correr:  E2E=1 python3 -m pytest tests/e2e -q        (levanta la app en local, en modo demo)
         E2E_URL=https://mi-app.up.railway.app python3 -m pytest tests/e2e -q -k solo_lectura
"""
import csv
import io
import os
import re

import pytest

LOCAL = not os.environ.get("E2E_URL")
solo_local = pytest.mark.skipif(not LOCAL, reason="escribe en la sala y gasta llamadas de IA: solo contra la app local")


# --- Solo lectura (sirven también contra un despliegue) ---------------------------------------------
def test_solo_lectura_la_app_responde_y_el_panel_1_se_llama_envia_facturas(sala):
    assert sala.pg.title() == "Envía facturas"
    assert "Envía facturas" in sala.texto() and sala.codigo


def test_solo_lectura_el_panel_1_no_muestra_reglas_ni_limites(sala):
    t = sala.texto().lower()
    for secreto in ("autopago", "reglas vigentes", "techo duro", "presupuesto del mes", "persona de finanzas"):
        assert secreto not in t


def test_solo_lectura_el_panel_2_entra_como_persona_con_punto_rojo(sala):
    sala.ir("Tablero")
    assert re.search(r"Persona de finanzas 🔴 \d+", sala.texto()) and re.search(r"Senior de finanzas 🔴 \d+", sala.texto())
    assert "Panel 2 · Finanzas › Tablero" in sala.texto()
    assert re.search(r"🔴 \d+ aprobación", sala.texto())                  # aviso en el menú lateral


def test_solo_lectura_el_calendario_navega_a_los_meses_futuros(sala):
    sala.ir("Calendario")
    assert "Octubre 2026" in sala.texto()
    sala.pg.get_by_role("button", name="Siguiente ▶").click()
    sala.pg.get_by_text("Noviembre 2026 · días hábiles").wait_for()
    assert "No hay obligaciones esperadas" not in sala.texto()
    for mes in ("Diciembre 2026", "Enero 2027"):                            # se espera cada mes antes de seguir
        sala.pg.get_by_role("button", name="Siguiente ▶").click()
        sala.pg.get_by_text(f"{mes} · días hábiles").wait_for()
    assert "No hay obligaciones esperadas este mes" in sala.texto()
    sala.pg.get_by_role("button", name="◀ Anterior").click()
    sala.pg.get_by_text("Diciembre 2026 · días hábiles").wait_for()


def test_solo_lectura_el_acta_de_una_sala_nueva_tiene_la_cadena_verificada(sala):
    sala.ir("Acta")
    sala.pg.get_by_text("Cadena verificada").wait_for()
    assert "filas con la huella correcta" in sala.texto()


# --- Recorrido del proveedor ----------------------------------------------------------------------------
@solo_local
def test_el_proveedor_sube_una_factura_repetida_y_queda_resuelta_y_frenada(sala):
    sala.subir("repetida.txt")
    t = sala.texto()
    assert "F-2001" in t and "Recibí tu factura TA-0931" in t and "Tu factura quedó resuelta" in t
    sala.ir("Cola_de_aprobacion")
    assert "F-2001" not in sala.texto()                                    # frenada: no espera aprobación
    sala.ir("Acta")
    sala.pg.get_by_text("Cadena verificada").wait_for()


@solo_local
def test_sin_ia_una_factura_normal_nunca_se_paga_sola_y_queda_en_revision(sala):
    sala.subir("normal.txt")
    t = sala.texto()
    assert "Tu factura quedó en revisión" in t and "Tu factura quedó resuelta" not in t
    sala.ir("Acta")
    with sala.pg.expect_download() as d:
        sala.pg.get_by_role("button", name="Descargar pagos_aprobados.csv").click()
    filas = list(csv.DictReader(io.StringIO(open(d.value.path(), encoding="utf-8").read())))
    assert "F-2001" not in [f.get("factura") for f in filas]               # lo escalado no sale en el archivo de pagos


@solo_local
def test_una_orden_escondida_en_la_factura_se_ignora_y_se_escala(sala):
    sala.subir("orden_escondida.txt")
    sala.ir("Cola_de_aprobacion")
    t = sala.texto()
    assert "F-1047" in t and "traía una orden; se ignoró" in t


# --- Recorrido de finanzas --------------------------------------------------------------------------------
@solo_local
def test_la_persona_aprueba_con_motivo_y_queda_en_el_acta_y_en_el_archivo_de_pagos(sala):
    sala.ir("Cola_de_aprobacion")
    assert "F-1043" in sala.texto() and "F-1045" not in sala.texto()       # la persona no ve lo del senior
    sala.pg.get_by_role("textbox", name="Motivo de tu decisión (obligatorio)").first.fill("Revisé el contrato")
    sala.pg.keyboard.press("Control+Enter")
    sala.pg.wait_for_timeout(800)
    sala.pg.get_by_role("button", name="Aprobar").first.click()
    sala.pg.get_by_text("F-1043 aprobada (pago de práctica)").wait_for()
    assert "Quedó en el acta, fila #" in sala.texto()
    sala.ir("Acta")
    sala.pg.get_by_text("Cadena verificada").wait_for()
    with sala.pg.expect_download() as d:
        sala.pg.get_by_role("button", name="Descargar pagos_aprobados.csv").click()
    texto = open(d.value.path(), encoding="utf-8").read()
    assert "F-1043" in texto and "supuesto" in texto.lower()


@solo_local
def test_aprobar_sin_motivo_se_rechaza_y_no_se_registra_nada(sala):
    sala.ir("Cola_de_aprobacion")
    sala.pg.get_by_role("button", name="Aprobar").first.click()
    sala.pg.wait_for_timeout(2500)
    assert "aprobada (pago de práctica)" not in sala.texto()
    sala.ir("Cola_de_aprobacion")
    assert "F-1043" in sala.texto()                                         # sigue pendiente


@solo_local
def test_el_senior_ve_lo_suyo_y_puede_rechazar(sala):
    sala.ir("Cola_de_aprobacion")
    sala.rol("Senior de finanzas")
    assert "F-1045" in sala.texto() and "Nuevo Proveedor SAS" in sala.texto()
    cajas = sala.pg.get_by_role("textbox", name="Motivo de tu decisión (obligatorio)")
    cajas.nth(1).fill("Proveedor sin validar")                             # F-1045 es la 2.ª de la cola del senior
    sala.pg.keyboard.press("Control+Enter")
    sala.pg.wait_for_timeout(800)
    sala.pg.get_by_role("button", name="Rechazar").nth(1).click()
    sala.pg.get_by_text("rechazada. Quedó en el acta").wait_for()


@solo_local
def test_la_persona_no_afloja_una_regla_y_el_senior_si(sala):
    sala.ir("Reglas")
    sala.pg.get_by_label("Pago automático hasta (USD)").fill("1000")
    sala.pg.keyboard.press("Enter")
    sala.pg.get_by_text("Este cambio afloja", exact=False).first.wait_for()
    sala.pg.get_by_role("textbox", name="Motivo del cambio (obligatorio)").fill("Más autonomía")
    sala.pg.keyboard.press("Control+Enter")
    sala.pg.wait_for_timeout(800)
    sala.pg.get_by_role("button", name="Confirmar cambio").click()
    sala.pg.get_by_text("solo el senior de finanzas puede firmarlo").first.wait_for()
    assert "Reglas cambiadas" not in sala.texto()
    sala.rol("Senior de finanzas")
    sala.pg.get_by_label("Pago automático hasta (USD)").fill("1000")
    sala.pg.keyboard.press("Enter")
    sala.pg.get_by_role("textbox", name="Motivo del cambio (obligatorio)").fill("Más volumen")
    sala.pg.keyboard.press("Control+Enter")
    sala.pg.wait_for_timeout(800)
    sala.pg.get_by_role("button", name="Confirmar cambio").click()
    sala.pg.get_by_text("Reglas cambiadas. Quedó en el acta").wait_for()


@solo_local
def test_pedir_un_cambio_con_texto_solo_rellena_el_formulario_sin_ia(sala):
    sala.ir("Reglas")
    sala.pg.get_by_role("textbox", name="Tu pedido").fill("sube el presupuesto un 20 %")
    sala.pg.keyboard.press("Control+Enter")
    sala.pg.wait_for_timeout(800)
    sala.pg.get_by_role("button", name="Entender el pedido").click()
    sala.pg.get_by_text("por patrones (sin IA)").wait_for()
    assert "25.000 USD → 30.000 USD" in sala.texto()
    assert "Reglas cambiadas" not in sala.texto()                          # entender no aplica nada
