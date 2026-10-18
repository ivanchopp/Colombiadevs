"""Spec motor-de-reglas R4.4 a R4.6 (P34): el nombre del beneficiario sin mayúsculas, tildes ni puntuación."""
from datetime import date

import pytest
from hypothesis import given, settings, strategies as st

from acta.estado import facturas_por_estado
from agents import flujo
from engine.contexto import contexto_desde_acta
from engine.evaluar import asociar_beneficiario, evaluar
from engine.guardarrail import registrar_decision
from engine.modelos import Ficha, Registro
from engine.reglas_io import cargar_contexto_base, cargar_reglas
from engine.revisiones.comun import clave_nombre, nombre_registrado
from tests.test_agente_entrada import ClienteFalso, sin_clave  # noqa: F401 (fixture autouse)
from tests.test_motor import con_historial, ficha, mov

HOY = date(2026, 10, 17)
EXACTO = "Tecnología Cafetera S.A.S."


@pytest.fixture
def reglas():
    return cargar_reglas(HOY)[0]


@pytest.fixture
def ctx():
    return cargar_contexto_base(HOY)


def regla(r, codigo):
    return next(x for x in r.revisiones if x.regla == codigo)


# --- R4.4: la asociación ------------------------------------------------------------------------
@pytest.mark.parametrize("variante", [
    "TECNOLOGÍA CAFETERA S.A.S.", "tecnologia cafetera s.a.s.", "Tecnología Cafetera SAS", "Tecnología  Cafetera   S.A.S.",
    "  Tecnología Cafetera S.A.S  ", "TECNOLOGIA CAFETERA S.A.S", "Tecnología, Cafetera, S.A.S.",
])
def test_r4_4_una_variante_de_mayusculas_tildes_o_puntuacion_es_el_mismo_proveedor(ctx, reglas, variante):
    r = evaluar(ficha(beneficiario=variante), ctx, reglas)
    exacto = evaluar(ficha(), ctx, reglas)
    assert (r.decision, r.nivel) == (exacto.decision, exacto.nivel) == ("PAGAR", "NINGUNO")
    assert regla(r, "R4.1").resultado == "OK" and f"leído como «{variante}»" in regla(r, "R4.1").mensaje


def test_r4_4_el_nombre_exacto_no_cambia_ni_dice_leido_como(ctx, reglas):
    r = evaluar(ficha(), ctx, reglas)
    assert "leído como" not in regla(r, "R4.1").mensaje


def test_r4_4_la_ficha_asociada_lleva_el_nombre_registrado_y_conserva_lo_leido(ctx):
    f = asociar_beneficiario(Ficha.model_validate(ficha(beneficiario="TECNOLOGÍA CAFETERA SAS")), ctx)
    assert f.beneficiario == EXACTO and f.beneficiario_leido == "TECNOLOGÍA CAFETERA SAS"
    exacta = asociar_beneficiario(Ficha.model_validate(ficha()), ctx)
    assert exacta.beneficiario_leido is None


@pytest.mark.parametrize("nombre", [
    "Tecnología Cafetera S.A.S. Colombia", "Tecnología Cafetera Ltda", "Tecnologia Cafetera Sucursal", "Cafetera Tecnología S.A.S.",
    "Tecnologa Cafetera S.A.S.", "Desconocido SAS",
])
def test_r4_6_no_se_asocia_por_parecido(ctx, reglas, nombre):
    r = evaluar(ficha(beneficiario=nombre), ctx, reglas)
    assert nombre_registrado(nombre, ctx) is None
    assert (r.decision, r.nivel) == ("ESCALAR", "SENIOR") and regla(r, "R4.1").resultado == "FALLA"


def test_r4_4_si_dos_proveedores_normalizan_igual_no_se_asocia_ninguno(ctx, reglas):
    doble = ctx.model_copy(update={"registros": {**ctx.registros, "ACME S.A.S.": Registro(pais="CO", cuenta="Cuenta demo ···9001"),
                                                  "Acme SAS": Registro(pais="CO", cuenta="Cuenta demo ···9002")}})
    assert nombre_registrado("acme sas", doble) is None
    assert nombre_registrado("Acme SAS", doble) == "Acme SAS"                    # el nombre exacto siempre vale
    r = evaluar(ficha(beneficiario="acme sas", cuenta_original="Cuenta demo ···9001"), doble, reglas)
    assert (r.decision, r.nivel) == ("ESCALAR", "SENIOR") and regla(r, "R4.1").resultado == "FALLA"


def test_r4_4_clave_nombre():
    assert clave_nombre("  ÁÉÍ, Ñandú  S.A.S. ") == "aei nandu sas"
    assert clave_nombre("...") == ""
    assert nombre_registrado("...", cargar_contexto_base(HOY)) is None


# --- R4.5: nada más cambia ---------------------------------------------------------------------
def test_r4_5_la_cuenta_se_sigue_comparando_con_la_registrada(ctx, reglas):
    r = evaluar(ficha(beneficiario="TECNOLOGÍA CAFETERA SAS", cuenta_original="Cuenta demo ···0001"), ctx, reglas)
    assert (r.decision, r.nivel) == ("ESCALAR", "SENIOR") and regla(r, "R4.2").resultado == "FALLA"


def test_r4_5_el_historial_y_el_limite_cuentan_bajo_un_solo_nombre(ctx, reglas):
    previo = con_historial(ctx, mov(EXACTO, 2_000_000))                       # pagado antes, con el nombre registrado
    a = evaluar(ficha(beneficiario="TECNOLOGÍA CAFETERA SAS"), previo, reglas)
    b = evaluar(ficha(), previo, reglas)
    assert (a.decision, a.nivel, a.monto_base) == (b.decision, b.nivel, b.monto_base)
    assert [x.regla + x.resultado for x in a.revisiones] == [x.regla + x.resultado for x in b.revisiones]


def test_r4_5_una_factura_repetida_se_detecta_aunque_cambie_la_forma_del_nombre(ctx, reglas):
    repetida = con_historial(ctx, mov(EXACTO, 2_400_000, fid="H9", numero="PN-T1", vence="2026-10-22"))
    r = evaluar(ficha(beneficiario="TECNOLOGÍA CAFETERA SAS"), repetida, reglas)
    assert r.decision == "FRENAR" and regla(r, "R3.1").resultado == "FALLA"


def test_r4_5_una_variante_no_aflojaba_nada_que_el_nombre_exacto_no_aflojara(ctx, reglas):
    for cambios in (dict(monto="9000000"), dict(recibida="2026-10-01"), dict(segunda_lectura="no_coincide"),
                    dict(lectura_ia="dudosa"), dict(orden_en_texto=True), dict(moneda="JPY")):
        a = evaluar(ficha(beneficiario="TECNOLOGÍA CAFETERA SAS", **cambios), ctx, reglas)
        b = evaluar(ficha(**cambios), ctx, reglas)
        assert (a.decision, a.nivel) == (b.decision, b.nivel), cambios


# --- El acta lleva el nombre registrado ---------------------------------------------------------
def test_r4_4_el_acta_guarda_el_nombre_registrado_y_lo_leido(almacen, sala, ctx, reglas):
    fila = registrar_decision(almacen, sala, ficha(beneficiario="TECNOLOGÍA CAFETERA SAS"), ctx, reglas)
    assert fila.payload["beneficiario"] == EXACTO
    assert fila.payload["ficha"]["beneficiario"] == EXACTO and fila.payload["ficha"]["beneficiario_leido"] == "TECNOLOGÍA CAFETERA SAS"
    assert fila.payload["pais"] == "CO"                                          # el registro se encontró
    base = contexto_desde_acta(cargar_contexto_base(HOY), almacen.filas(sala))
    assert any(m.beneficiario == EXACTO and m.factura_id == "T1" for m in base.historial)


# --- De punta a punta: una factura con el nombre en mayúsculas ----------------------------------
def test_p34_una_factura_con_el_nombre_en_mayusculas_decide_igual_que_con_el_nombre_exacto(almacen, sala, monkeypatch):
    monkeypatch.setenv("FECHA_DEMO", "2026-10-17")
    monkeypatch.setenv("FACTURAS_MAX", "20")
    texto = (b"FACTURA No.: AV-7781\nEmisor: ALIMENTOS DEL VALLE S.A.S.\nNIT: 926204505-3\nVence: 2026-10-31\n"
             b"Total: 1.800.000 COP\nCuenta: Cuenta demo \xc2\xb7\xc2\xb7\xc2\xb70026\n")
    lectura = dict(beneficiario="ALIMENTOS DEL VALLE S.A.S.", numero="AV-7781", monto="1800000", moneda="COP",
                   vence="2026-10-31", cuenta="Cuenta demo ···0026", id_tributaria="926204505-3", dudosos=[])
    e = flujo.recibir(almacen, sala, "mayusculas.txt", texto, cliente=ClienteFalso(lectura))
    d = facturas_por_estado(almacen.filas(sala))[e["factura_id"]].decision
    assert (d["decision"], d["nivel"]) == ("PAGAR", "NINGUNO")
    assert d["beneficiario"] == "Alimentos del Valle S.A.S." and d["ficha"]["beneficiario_leido"] == "ALIMENTOS DEL VALLE S.A.S."


# --- Propiedad: una variante nunca decide distinto que el nombre exacto -------------------------
VIOLACIONES = [dict(), dict(monto="9000000"), dict(recibida="2026-10-01"), dict(segunda_lectura="no_coincide"),
               dict(lectura_ia="dudosa"), dict(orden_en_texto=True), dict(moneda="JPY"), dict(cuenta_original="Cuenta demo ···0001"),
               dict(cuenta_aclarada="Cuenta demo ···0002"), dict(origen_campos={"numero": "aclarado"})]


def variante(nombre, modo):
    sin = nombre.translate(str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU"))
    return {0: nombre.upper(), 1: nombre.lower(), 2: nombre.replace(".", ""), 3: sin, 4: "  " + nombre.replace(" ", "  ") + " ",
            5: nombre.replace(".", ",").upper()}[modo]


@settings(max_examples=250, deadline=None)
@given(st.sampled_from(VIOLACIONES), st.integers(0, 5))
def test_r4_5_una_variante_del_nombre_nunca_decide_distinto_que_el_nombre_exacto(violacion, modo):
    ctx, reglas = cargar_contexto_base(HOY), cargar_reglas(HOY)[0]
    a = evaluar(ficha(beneficiario=variante(EXACTO, modo), **violacion), ctx, reglas)
    b = evaluar(ficha(**violacion), ctx, reglas)
    assert (a.decision, a.nivel) == (b.decision, b.nivel)
