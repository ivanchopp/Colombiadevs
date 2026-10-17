"""R11.3 y R11.4: las 20 facturas de prueba (la misma medición que eval.py)."""
import eval as evaluacion


def test_r11_3_los_20_casos_dan_lo_esperado():
    filas = evaluacion.correr()
    assert len(filas) == 20
    malos = [(f["caso"]["id"], f["resultado"].decision, f["resultado"].nivel) for f in filas if not f["bien"]]
    assert malos == []


def test_cero_pagos_indebidos():
    assert not any(f["indebido"] for f in evaluacion.correr())


def test_r11_4_menos_de_200_ms():
    assert max(f["ms"] for f in evaluacion.correr()) < 200
