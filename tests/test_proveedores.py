"""Spec ordenes-de-compra, OC1: registro de proveedores generado desde el listado del equipo."""
from collections import Counter
from pathlib import Path

import pytest
import yaml

from data.importar_compras import formato_valido, proveedores_desde_filas

PROVS = yaml.safe_load((Path(__file__).resolve().parent.parent / "data" / "proveedores.yaml").read_text(encoding="utf-8"))


def test_oc1_1_campos_y_cuenta_ficticia():
    p = PROVS["proveedores"]
    assert PROVS["supuesto"] is True and len(p) == 200
    assert all(set(x) == {"id", "nombre", "pais", "id_tributaria", "tipo_id", "cuenta", "marcas"} for x in p)
    assert all(x["cuenta"].startswith("Cuenta demo") for x in p)
    assert len({x["id"] for x in p}) == 200 and len({x["nombre"] for x in p}) == 200


def test_oc1_2_sin_datos_de_contacto():
    texto = yaml.safe_dump(PROVS, allow_unicode=True)
    assert "@" not in texto and "+57" not in texto and "+52" not in texto


def test_oc1_3_y_oc1_4_marcas_del_listado():
    marcas = Counter(m for x in PROVS["proveedores"] for m in x["marcas"])
    assert marcas == {"identificacion_repetida": 20, "identificacion_invalida": 30}


@pytest.mark.parametrize("tipo, pais, valor, esperado", [
    ("NIT", "Colombia", "900123456-7", True), ("NIT", "Colombia", "FALLA-999999-X", False),
    ("RFC", "México", "TAV120405H87", True), ("RUC", "Perú", "20554433221", True),
    ("RUC", "Perú", "2010000008", False), ("RUC", "Ecuador", "1791234567001", True),
    ("RUC", "Ecuador", "179100009001", False),
])
def test_oc1_4_formato(tipo, pais, valor, esperado):
    assert formato_valido(tipo, pais, valor) is esperado


def test_oc1_3_repetida_y_numero_leido_como_texto():
    provs = proveedores_desde_filas([(1, "A", "Perú", 20554433221, "RUC"), (2, "B", "Perú", "20554433221", "RUC")])
    assert all(p["id_tributaria"] == "20554433221" and p["marcas"] == ["identificacion_repetida"] for p in provs)


def test_id_o_nombre_repetido_se_rechaza():
    with pytest.raises(ValueError):
        proveedores_desde_filas([(1, "A", "Perú", "1", "RUC"), (1, "B", "Perú", "2", "RUC")])
