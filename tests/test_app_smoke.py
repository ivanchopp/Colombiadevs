from pathlib import Path

from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]
PROHIBIDAS = ("umbral", "límite", "limite", "regla")


def test_panel1_sin_sala():
    at = AppTest.from_file(str(RAIZ / "app/main.py")).run()
    assert not at.exception
    texto = " ".join(e.value for e in at.markdown).lower()
    assert not any(p in texto for p in PROHIBIDAS)


def test_panel1_sala_invalida():
    at = AppTest.from_file(str(RAIZ / "app/main.py"))
    at.query_params["sala"] = "mala"
    at.run()
    assert not at.exception and at.warning


def test_panel2_sin_sala_se_detiene():
    at = AppTest.from_file(str(RAIZ / "app/pages/1_Finanzas.py")).run()
    assert not at.exception and at.warning
