"""R4: la moneda base es configurable y ninguna pieza supone una fija (R5.6 a R5.8)."""
import re
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from engine.evaluar import evaluar
from engine.reglas_io import cargar_contexto_base, cargar_reglas
from tests.test_motor import ficha

HOY = date(2026, 10, 17)
RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture
def base():
    return cargar_contexto_base(HOY), cargar_reglas(HOY)[0]


def test_r5_6_la_base_de_demo_es_usd(base):
    ctx, reglas = base
    assert reglas.moneda_base == "USD" and ctx.tasas["USD"] == 1


def test_r5_6_con_otra_base_los_mensajes_la_usan(base):
    """Se pasa a EUR (solo configuración): los textos de las revisiones hablan de EUR, no de USD ni de COP."""
    ctx, reglas = base
    en_eur = {k: v / ctx.tasas["EUR"] for k, v in ctx.tasas.items()}            # EUR vale 1
    r = evaluar(ficha(), ctx.model_copy(update={"tasas": en_eur}), reglas.model_copy(update={"moneda_base": "EUR"}))
    textos = " ".join(f"{x.observado} {x.umbral} {x.mensaje}" for x in r.revisiones if x.regla in ("R3.6", "R3.7", "R5.1", "R5.3", "R5.4"))
    assert "EUR" in textos and "USD" not in textos and "COP" not in textos


def test_r5_7_tabla_de_cambio_que_no_coincide_con_la_base_escala_y_no_paga(base):
    ctx, reglas = base
    mala = ctx.model_copy(update={"tasas": {**ctx.tasas, "USD": Decimal("1.01")}})        # la base ya no vale 1
    r = evaluar(ficha(), mala, reglas)
    falla = next(x for x in r.revisiones if x.regla == "R5.7")
    assert r.decision == "ESCALAR" and r.nivel == "SENIOR" and falla.resultado == "FALLA"
    assert "no coincide con la moneda base" in falla.mensaje


def test_r5_7_sin_tasa_para_la_base_tampoco_paga(base):
    ctx, reglas = base
    sin = ctx.model_copy(update={"tasas": {k: v for k, v in ctx.tasas.items() if k != "USD"}})
    assert evaluar(ficha(), sin, reglas).decision == "ESCALAR"


def test_r5_6_el_codigo_no_supone_la_moneda_base():
    """Ninguna pantalla ni regla del motor lleva «COP» o «USD» escrito como moneda base."""
    ofensores = []
    for carpeta in ("engine", "app", "acta"):
        for ruta in (RAIZ / carpeta).rglob("*.py"):
            for n, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
                if re.search(r"""['"](COP|USD)['"]""", linea) and "moneda_base" not in linea and "#" not in linea:
                    ofensores.append(f"{ruta.relative_to(RAIZ)}:{n}: {linea.strip()}")
    assert not ofensores, "\n".join(ofensores)
