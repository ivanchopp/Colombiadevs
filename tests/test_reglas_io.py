from engine.reglas_io import cargar_reglas, cargar_reglas_o_anterior


def test_archivo_invalido_conserva_anterior(tmp_path):
    anterior = cargar_reglas()
    malo = tmp_path / "r.yaml"
    malo.write_text("version: v2\nextra: 1\n", encoding="utf-8")
    r, error = cargar_reglas_o_anterior(malo, anterior)
    assert r is anterior and error


def test_archivo_inexistente(tmp_path):
    anterior = cargar_reglas()
    r, error = cargar_reglas_o_anterior(tmp_path / "no.yaml", anterior)
    assert r is anterior and error
