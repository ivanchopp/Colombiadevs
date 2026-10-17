from decimal import Decimal

from engine.niveles import nivel_maximo, nivel_por_monto
from engine.reglas_io import cargar_reglas


def test_limites():
    r = cargar_reglas()
    assert nivel_por_monto(Decimal("3000000"), r) == "NINGUNO"
    assert nivel_por_monto(Decimal("3000001"), r) == "PERSONA"
    assert nivel_por_monto(Decimal("10000000"), r) == "PERSONA"
    assert nivel_por_monto(Decimal("10000001"), r) == "SENIOR"


def test_maximo():
    assert nivel_maximo([]) == "NINGUNO"
    assert nivel_maximo(["PERSONA", "SENIOR", "NINGUNO"]) == "SENIOR"
