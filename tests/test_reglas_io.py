from datetime import date
from decimal import Decimal
from pathlib import Path
import shutil

import pytest

from engine.reglas_io import ErrorDeReglas, cargar_reglas

HOY = date(2026, 10, 17)
DATA = Path(__file__).resolve().parent.parent / "data"


def test_r9_3_la_version_viaja_con_las_reglas():
    assert cargar_reglas(HOY)[0].version == "v12"


def test_r9_1_yaml_invalido_conserva_la_anterior(tmp_path):
    anterior = cargar_reglas(HOY)[0]
    shutil.copy(DATA / "techos.yaml", tmp_path / "techos.yaml")
    (tmp_path / "reglas.yaml").write_text("conjuntos:\n  - {version: v13, vigente_desde: 2026-10-01, autopago_max: abc}\n")
    reglas, error = cargar_reglas(HOY, tmp_path, anterior)
    assert reglas.version == "v12" and error
    with pytest.raises(ErrorDeReglas):
        cargar_reglas(HOY, tmp_path)


def test_r9_2_se_aplica_la_version_vigente(tmp_path):
    shutil.copy(DATA / "techos.yaml", tmp_path / "techos.yaml")
    texto = (DATA / "reglas.yaml").read_text()
    nuevo = texto.replace("v12", "v13").replace("2026-10-01", "2026-10-20").replace("  - version", "  - version")
    (tmp_path / "reglas.yaml").write_text(texto + nuevo.split("conjuntos:\n")[1])
    assert cargar_reglas(date(2026, 10, 17), tmp_path)[0].version == "v12"
    assert cargar_reglas(date(2026, 10, 21), tmp_path)[0].version == "v13"


def test_r9_5_el_techo_duro_manda(tmp_path):
    shutil.copy(DATA / "techos.yaml", tmp_path / "techos.yaml")
    texto = (DATA / "reglas.yaml").read_text().replace('techo_duro_pago: "12500"', 'techo_duro_pago: "22500"')
    (tmp_path / "reglas.yaml").write_text(texto)
    assert cargar_reglas(HOY, tmp_path)[0].techo_duro_pago == Decimal("12500")
