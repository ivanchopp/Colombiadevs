import pytest

from acta.exportar_csv import seguro


@pytest.mark.parametrize("c", ["=1+1", "+1", "-1", "@SUM(A1)"])
def test_neutraliza(c):
    assert seguro(c) == "'" + c


def test_texto_normal():
    assert seguro("Acme") == "Acme"
