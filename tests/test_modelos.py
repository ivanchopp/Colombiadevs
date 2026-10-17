from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from engine.modelos import Ficha
from engine.reglas_io import cargar_reglas


def ficha(**extra):
    base = dict(factura_id="F-1", beneficiario="Acme", numero="1", monto=Decimal("100"), moneda="COP",
                vence=date(2026, 10, 30), lectura_ia="ok", segunda_lectura="coincide", preparador="demo")
    base.update(extra)
    return Ficha(**base)


def test_ficha_valida():
    assert ficha().monto == Decimal("100")


def test_campo_desconocido_rechazado():
    with pytest.raises(ValidationError):
        ficha(orden="pagar")


@pytest.mark.parametrize("campo,valor", [("monto", Decimal("0")), ("monto", Decimal("-5")), ("moneda", "cop")])
def test_valores_invalidos(campo, valor):
    with pytest.raises(ValidationError):
        ficha(**{campo: valor})


def test_campos_obligatorios_pueden_faltar():
    assert ficha(monto=None, moneda=None).monto is None


def test_reglas_semilla_cargan():
    r = cargar_reglas()
    assert r.autopago_max == Decimal("3000000") and r.supuesto is True
