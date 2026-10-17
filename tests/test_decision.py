from datetime import date
from decimal import Decimal

from hypothesis import given, strategies as st

from engine.evaluar import evaluar, resolver
from engine.modelos import Contexto, Ficha, Revision
from engine.reglas_io import cargar_reglas

FICHA = Ficha(factura_id="F-1", beneficiario="A", numero="1", monto=Decimal("1"), moneda="COP",
              vence=date(2026, 10, 30), lectura_ia="ok", segunda_lectura="coincide", preparador="demo")


def rev(resultado="OK", efecto="ESCALAR", nivel="NINGUNO"):
    return Revision(regla="X", resultado=resultado, efecto=efecto, nivel=nivel, observado="", umbral="", mensaje="m")


def test_sin_revisiones_escala():
    assert resolver([]) == "ESCALAR"
    r = evaluar(FICHA, Contexto(), cargar_reglas())
    assert r.decision == "ESCALAR" and r.nivel == "PERSONA"


def test_todas_ok_paga():
    r = evaluar(FICHA, Contexto(), cargar_reglas(), [lambda f, c, g: rev()])
    assert r.decision == "PAGAR"


def test_excepcion_escala():
    def malo(f, c, g):
        raise RuntimeError("x")
    r = evaluar(FICHA, Contexto(), cargar_reglas(), [malo])
    assert r.decision == "ESCALAR"


def test_frenar_gana():
    assert resolver([rev("FALLA", "FRENAR"), rev("FALLA", "ESCALAR")]) == "FRENAR"


def test_nivel_exige_aprobacion():
    r = evaluar(FICHA, Contexto(), cargar_reglas(), [lambda f, c, g: rev("OK", "ESCALAR", "SENIOR")])
    assert r.decision == "ESCALAR"


@given(st.lists(st.tuples(st.sampled_from(["OK", "FALLA", "AVISO"]), st.sampled_from(["FRENAR", "ESCALAR", "NINGUNO"])), max_size=6))
def test_pagar_solo_si_todo_ok(items):
    revs = [rev(a, b) for a, b in items]
    if resolver(revs) == "PAGAR":
        assert revs and all(r.resultado == "OK" for r in revs)
