"""Spec ordenes-de-compra (versión mínima): OC1 a OC5, OC7 y OC8 con órdenes sintéticas."""
from datetime import date
from decimal import Decimal

import pytest
import yaml
from hypothesis import given, settings, strategies as st

from acta.estado import facturas_por_estado
from engine.compras import (ErrorDeCompras, cargar_compras, normalizar_oc, registros_de_proveedores,
                            validar_ordenes)
from engine.contexto import contexto_desde_acta
from engine.evaluar import evaluar
from engine.guardarrail import registrar_decision
from engine.modelos import Obligacion, OrdenCompra
from engine.reglas_io import DATA, cargar_contexto_base, cargar_reglas
from tests.test_motor import ficha

HOY = date(2026, 10, 17)
HUILA, LABS, ALIMENTOS = ("Agroindustrias del Huila S.A.S.", "Laboratorios Clínicos Cundinamarca S.A.S.",
                          "Corporación Alimentarios Orinoquía S.A.S.")
ECUADOR_INVALIDO = "Corporación Importadora del Ecuador Corp. Bl. 19"


@pytest.fixture
def reglas():
    return cargar_reglas(HOY)[0]


@pytest.fixture
def ctx():
    """Contexto base más una obligación en el calendario para cada factura de prueba con OC."""
    base = cargar_contexto_base(HOY)
    cal = [Obligacion(id=f"OC-{i}", beneficiario=n, fecha=date(2026, 10, 15), monto_base=Decimal(m))
           for i, (n, m) in enumerate([(HUILA, "1160000"), (HUILA, "1252800"), (LABS, "1160000")])]
    return base.model_copy(update={"calendario": base.calendario + cal})


def f_oc(**cambios):
    base = dict(factura_id="T-OC", beneficiario=HUILA, numero="H-1", monto="1160000", vence="2026-10-30",
                recibida="2026-10-15", cuenta_original="Cuenta demo ···0005", orden_compra="PO-2026-001",
                id_tributaria="999016272-1")
    base.update(cambios)
    return ficha(**base)


def regla(r, codigo):
    return next(x for x in r.revisiones if x.regla == codigo)


# --- OC1 y OC2: datos --------------------------------------------------------------------------
def test_oc1_los_proveedores_se_suman_a_los_beneficiarios_actuales(ctx):
    assert "Pixel Norte Ltda." in ctx.registros and HUILA in ctx.registros          # OCD4
    assert ctx.registros[HUILA].pais == "CO" and ctx.registros[HUILA].acuerdo_monto is None
    assert len(ctx.proveedores) == 200


def test_oc1_los_registros_actuales_no_se_pisan():
    proveedores = cargar_contexto_base(HOY).proveedores
    existentes = {"Pixel Norte Ltda.": object(), proveedores[0].nombre: object()}
    assert proveedores[0].nombre not in registros_de_proveedores(proveedores, existentes)


def test_oc2_las_ordenes_sinteticas_cargan_y_marcan_la_identificacion_distinta(ctx):
    assert len(ctx.ordenes) == 8
    assert ctx.ordenes["PO2026021"].marcas == ["no_coincide_con_proveedor"]        # OC2.3
    assert ctx.ordenes["PO2026001"].marcas == []


def test_oc2_2_se_rechaza_numero_repetido_proveedor_inexistente_o_cuentas_malas(ctx):
    oc = ctx.ordenes["PO2026001"]
    with pytest.raises(ErrorDeCompras, match="repetida"):
        validar_ordenes([oc, oc], ctx.proveedores)
    with pytest.raises(ErrorDeCompras, match="no existe"):
        validar_ordenes([oc.model_copy(update={"proveedor_id": 99999})], ctx.proveedores)
    with pytest.raises(ErrorDeCompras, match="subtotal"):
        validar_ordenes([oc.model_copy(update={"subtotal": Decimal("1")})], ctx.proveedores)
    with pytest.raises(ErrorDeCompras, match="total"):
        validar_ordenes([oc.model_copy(update={"total": Decimal("1")})], ctx.proveedores)


def test_oc1_5_un_archivo_roto_deja_el_registro_vacio_y_toda_oc_escala(tmp_path, reglas, ctx):
    (tmp_path / "proveedores.yaml").write_text((DATA / "proveedores.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "ordenes_compra.yaml").write_text("ordenes: [{numero: X}]", encoding="utf-8")
    proveedores, ordenes = cargar_compras(tmp_path)
    assert len(proveedores) == 200 and ordenes == {}
    r = evaluar(f_oc(), ctx.model_copy(update={"ordenes": ordenes}), reglas)
    assert (r.decision, r.nivel) == ("ESCALAR", "SENIOR") and regla(r, "OC4.2").efecto == "ESCALAR"


def test_el_yaml_de_ordenes_dice_que_es_sintetico():
    datos = yaml.safe_load((DATA / "ordenes_compra.yaml").read_text(encoding="utf-8"))
    assert datos["sintetico"] is True and datos["supuesto"] is True


def test_normalizar_oc():
    assert {normalizar_oc(x) for x in ("po 2026 001", "PO-2026-001", "PO2026001")} == {"PO2026001"}


# --- OC4: la revisión --------------------------------------------------------------------------
def test_oc4_1_una_oc_que_cuadra_se_paga_y_hace_las_veces_de_acuerdo(ctx, reglas):
    r = evaluar(f_oc(), ctx, reglas)
    assert (r.decision, r.nivel) == ("PAGAR", "NINGUNO")
    assert regla(r, "OC4.1").resultado == "OK" and regla(r, "R3.5").resultado == "OK"


def test_oc4_1_el_numero_se_reconoce_escrito_de_otra_forma(ctx, reglas):
    assert evaluar(f_oc(orden_compra="po 2026 001"), ctx, reglas).decision == "PAGAR"


def test_oc4_2_oc_inexistente_va_al_senior(ctx, reglas):
    r = evaluar(f_oc(orden_compra="PO-2026-999"), ctx, reglas)
    assert (r.decision, r.nivel) == ("ESCALAR", "SENIOR") and "inexistente" in r.motivo


def test_oc4_3_oc_de_otro_proveedor_o_identificacion_distinta_va_al_senior(ctx, reglas):
    ajena = evaluar(f_oc(beneficiario=LABS, cuenta_original="Cuenta demo ···0008", id_tributaria="966177115-3"), ctx, reglas)
    otra_id = evaluar(f_oc(id_tributaria="999016272-9"), ctx, reglas)
    for r in (ajena, otra_id):
        assert (r.decision, r.nivel) == ("ESCALAR", "SENIOR") and regla(r, "OC4.3").resultado == "FALLA"


def test_oc4_3_sin_identificacion_en_la_factura_no_se_paga(ctx, reglas):
    r = evaluar(f_oc(id_tributaria=None), ctx, reglas)
    assert (r.decision, r.nivel) == ("ESCALAR", "PERSONA")


def test_oc4_4_oc_marcada_no_coincide_con_el_proveedor_va_al_senior(ctx, reglas):
    r = evaluar(f_oc(beneficiario="Soluciones Alimentarios Andino S.A.S.", orden_compra="PO-2026-021",
                     cuenta_original="Cuenta demo ···0023", id_tributaria="951552286-8"), ctx, reglas)
    assert (r.decision, r.nivel) == ("ESCALAR", "SENIOR")


@pytest.mark.parametrize("orden", [None, "PO-2026-020"])
def test_oc4_4_proveedor_con_identificacion_invalida_va_al_senior_cite_o_no_una_oc(ctx, reglas, orden):
    r = evaluar(f_oc(beneficiario=ECUADOR_INVALIDO, cuenta_original="Cuenta demo ···0002",
                     id_tributaria="179100019001", orden_compra=orden), ctx, reglas)
    assert (r.decision, r.nivel) == ("ESCALAR", "SENIOR") and regla(r, "OC4.4").resultado == "FALLA"


def test_oc4_5_de_5_a_10_por_ciento_escala_a_la_persona_y_mas_de_10_frena(ctx, reglas):
    medio = evaluar(f_oc(monto="1252800"), ctx, reglas)                      # +8 %
    alto = evaluar(f_oc(monto="1334000"), ctx, reglas)                       # +15 %
    assert (medio.decision, medio.nivel) == ("ESCALAR", "PERSONA")
    assert (alto.decision, alto.nivel) == ("FRENAR", "NINGUNO") and "orden de compra" in alto.motivo


def test_oc4_6_una_oc_ya_facturada_frena(ctx, reglas):
    usada = ctx.model_copy(update={"oc_facturadas": {"PO2026001": "F-OTRA"}})
    r = evaluar(f_oc(), usada, reglas)
    assert r.decision == "FRENAR" and regla(r, "OC4.6").efecto == "FRENAR"
    assert evaluar(f_oc(factura_id="F-OTRA"), usada, reglas).decision == "PAGAR"      # la misma factura no se frena sola


def test_oc4_7_otra_moneda_se_compara_en_moneda_base(ctx, reglas):
    oc_usd = OrdenCompra(numero="PO-USD", proveedor_id=5, id_tributaria="999016272-1", articulo="x", cantidad=1,
                         precio_unitario=Decimal("100"), subtotal=Decimal("100"), iva=Decimal("0"),
                         total=Decimal("100"), moneda="USD")
    c = ctx.model_copy(update={"ordenes": {**ctx.ordenes, "PO-USD".replace("-", ""): oc_usd},
                               "tasas": {k: v for k, v in ctx.tasas.items()}})
    r = evaluar(f_oc(orden_compra="PO-USD", monto="100", moneda="USD"), c, reglas)
    assert regla(r, "OC4.1").resultado == "OK"
    sin_tasa = c.model_copy(update={"tasas": {k: v for k, v in c.tasas.items() if k != "USD"}})
    r = evaluar(f_oc(orden_compra="PO-USD", monto="100", moneda="USD"), sin_tasa, reglas)
    assert r.decision == "ESCALAR"


def test_oc4_8_sin_oc_sigue_el_flujo_de_siempre(ctx, reglas):
    r = evaluar(ficha(), ctx, reglas)
    assert r.decision == "PAGAR" and regla(r, "OC4.8").resultado == "OK"


def test_oc4_9_una_oc_valida_no_salta_el_calendario_ni_los_niveles(ctx, reglas):
    fuera = evaluar(f_oc(recibida="2026-10-02"), ctx, reglas)                # sin obligación esperada
    assert (fuera.decision, fuera.nivel) == ("ESCALAR", "PERSONA") and regla(fuera, "R6.2").resultado == "AVISO"
    grande = ctx.model_copy(update={"ordenes": {"PO2026001": ctx.ordenes["PO2026001"].model_copy(update={
        "total": Decimal("5000000"), "subtotal": Decimal("4310344.83")})}})
    r = evaluar(f_oc(monto="5000000"), grande, reglas)
    assert r.decision != "PAGAR" and regla(r, "R5.3").resultado == "AVISO"


def test_oc4_9_el_acuerdo_registrado_sigue_aplicando_con_oc(ctx, reglas):
    r = evaluar(ficha(factura_id="T-AC", orden_compra="PO-2026-001", id_tributaria="999016272-1"), ctx, reglas)
    assert r.decision != "PAGAR"           # Pixel Norte no es el proveedor de la OC


# --- OC5: consumo desde el acta ---------------------------------------------------------------
def test_oc5_la_oc_queda_facturada_si_la_factura_queda_pendiente_y_libre_si_se_frena(almacen, ctx, reglas):
    sin_cal = cargar_contexto_base(HOY)
    registrar_decision(almacen, "SALA0001", f_oc(factura_id="F-1", recibida="2026-10-02"), sin_cal, reglas)   # PENDIENTE
    c = contexto_desde_acta(sin_cal, almacen.filas("SALA0001"))
    assert c.oc_facturadas == {"PO2026001": "F-1"}
    segunda = evaluar(f_oc(factura_id="F-2"), c, reglas)
    assert segunda.decision == "FRENAR"                                                       # OC4.6
    registrar_decision(almacen, "SALA0001", f_oc(factura_id="F-2"), c, reglas)                # queda FRENADA
    c2 = contexto_desde_acta(sin_cal, almacen.filas("SALA0001"))
    assert c2.oc_facturadas == {"PO2026001": "F-1"}                                           # FRENADA no la consume
    assert facturas_por_estado(almacen.filas("SALA0001"))["F-2"].estado == "FRENADA"


def test_oc5_3_la_decision_guarda_el_numero_de_oc(almacen, ctx, reglas):
    fila = registrar_decision(almacen, "SALA0002", f_oc(), ctx, reglas)
    assert fila.payload["ficha"]["orden_compra"] == "PO-2026-001" and fila.payload["decision"] == "PAGAR"


# --- OC8.2: propiedades -----------------------------------------------------------------------
VIOLACIONES_OC = {
    "inexistente": dict(orden_compra="PO-2026-999"),
    "ajena": dict(orden_compra="PO-2026-004"),
    "identificacion_distinta": dict(id_tributaria="000000000-0"),
    "sin_identificacion": dict(id_tributaria=None),
    "monto_alterado_8": dict(monto="1252800"),
    "monto_alterado_15": dict(monto="1334000"),
    "proveedor_invalido": dict(beneficiario=ECUADOR_INVALIDO, cuenta_original="Cuenta demo ···0002",
                               id_tributaria="179100019001", orden_compra="PO-2026-020"),
    "oc_con_id_distinta": dict(beneficiario="Soluciones Alimentarios Andino S.A.S.", orden_compra="PO-2026-021",
                               cuenta_original="Cuenta demo ···0023", id_tributaria="951552286-8"),
}


@settings(max_examples=200, deadline=None)
@given(st.sampled_from(sorted(VIOLACIONES_OC)), st.sampled_from(["ok", "dudosa"]), st.booleans())
def test_oc8_2_ninguna_violacion_de_la_oc_da_pagar(violacion, lectura, orden_escondida):
    base = cargar_contexto_base(HOY)
    ctx = base.model_copy(update={"calendario": base.calendario + [
        Obligacion(id="OC-H", beneficiario=HUILA, fecha=date(2026, 10, 15), monto_base=Decimal("1160000"))]})
    r = evaluar(f_oc(lectura_ia=lectura, orden_en_texto=orden_escondida, **VIOLACIONES_OC[violacion]), ctx,
                cargar_reglas(HOY)[0])
    assert r.decision != "PAGAR", (violacion, r.motivo)


def test_oc8_2_la_oc_ya_facturada_nunca_da_pagar(ctx, reglas):
    usada = ctx.model_copy(update={"oc_facturadas": {"PO2026001": "F-OTRA"}})
    assert evaluar(f_oc(), usada, reglas).decision != "PAGAR"
