from datetime import date

import pytest

from acta.estado import facturas_por_estado
from engine.contexto import contexto_desde_acta
from engine.evaluar import evaluar
from engine.guardarrail import (AprobacionRechazada, DecisionRechazada, registrar_decision,
                                validar_aprobacion)
from engine.reglas_io import cargar_contexto_base, cargar_reglas
from tests.test_motor import ficha

HOY = date(2026, 10, 17)


@pytest.fixture
def entorno(almacen):
    return cargar_contexto_base(HOY), cargar_reglas(HOY)[0]


def test_r8_1_no_se_escribe_un_pago_fuera_de_las_reglas(almacen, entorno):
    ctx, reglas = entorno
    mala = ficha(beneficiario="Nuevo SAS")
    falso = evaluar(ficha(), ctx, reglas)                  # alguien propone PAGAR (de otra ficha buena)
    assert falso.decision == "PAGAR"
    with pytest.raises(DecisionRechazada):
        registrar_decision(almacen, "SALA0001", mala, ctx, reglas, propuesto=falso)
    filas = almacen.filas("SALA0001")
    assert [f.tipo for f in filas] == ["INTENTO_RECHAZADO"]       # solo queda el intento


def test_r8_1_una_decision_buena_se_registra_con_su_motivo(almacen, entorno):
    ctx, reglas = entorno
    fila = registrar_decision(almacen, "SALA0002", ficha(), ctx, reglas)
    assert fila.payload["decision"] == "PAGAR" and fila.payload["version_reglas"] == "v12"
    assert fila.payload["revisiones"] and fila.payload["motivo"]


def test_ficha_invalida_no_se_registra(almacen, entorno):
    ctx, reglas = entorno
    with pytest.raises(Exception):
        registrar_decision(almacen, "SALA0003", ficha(monto="-1"), ctx, reglas)
    assert almacen.filas("SALA0003") == []


def test_contexto_desde_el_acta_cierra_el_calendario_y_suma_el_periodo(almacen, entorno):
    ctx, reglas = entorno
    registrar_decision(almacen, "SALA0004", ficha(), ctx, reglas)
    ctx2 = contexto_desde_acta(ctx, almacen.filas("SALA0004"))
    assert next(o for o in ctx2.calendario if o.id == "O1").factura_id == "T1"
    assert any(m.factura_id == "T1" and m.estado == "PAGADA" for m in ctx2.historial)
    # un segundo envío igual (otra factura) ya no encuentra la obligación libre (R6.3)
    r = evaluar(ficha(factura_id="T2", numero="PN-T2"), ctx2, reglas)
    assert any(x.regla == "R6.2" for x in r.revisiones)


def test_r8_2_validar_aprobacion():
    ok = dict(rol="SENIOR", nivel_exigido="SENIOR", motivo="ok", actor="Senior", preparador="p",
              monto_base=Decimal("1"), techo=Decimal("50000000"))
    validar_aprobacion(**ok)
    for cambio in ({"rol": "PERSONA"}, {"motivo": " "}, {"actor": "p"}):
        with pytest.raises(AprobacionRechazada):
            validar_aprobacion(**{**ok, **cambio})


def test_r8_3_el_techo_duro_no_se_aprueba():
    with pytest.raises(AprobacionRechazada):
        validar_aprobacion("SENIOR", "SENIOR", "ok", "Senior", "p", Decimal("50000001"), Decimal("50000000"))


from decimal import Decimal  # noqa: E402
