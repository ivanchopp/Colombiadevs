from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from acta.huella import contenido_canonico, huella, huella_inicial


def test_orden_de_claves_no_importa():
    assert contenido_canonico({"a": 1, "b": 2}) == contenido_canonico({"b": 2, "a": 1})


def test_formatos_canonicos():
    s = contenido_canonico({"m": Decimal("5"), "t": Decimal("0.1234567"), "d": date(2026, 10, 1),
                            "h": datetime(2026, 10, 1, 12, tzinfo=timezone.utc)}).decode()
    assert '"m":"5.00"' in s and '"t":"0.123457"' in s and '"d":"2026-10-01"' in s and "2026-10-01T12:00:00Z" in s


def test_fecha_sin_zona_falla():
    with pytest.raises(ValueError):
        contenido_canonico({"h": datetime(2026, 10, 1)})


def test_cadena_cambia_si_se_altera():
    h0 = huella_inicial("SALA")
    h1 = huella(h0, {"n": 1})
    assert h1 != huella(h0, {"n": 2}) and h1 != h0
    assert huella_inicial("A") != huella_inicial("B")
