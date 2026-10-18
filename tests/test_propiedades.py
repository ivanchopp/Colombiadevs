"""R11.2: cualquier ficha que viole una regla bloqueante nunca da PAGAR."""
from datetime import date

from hypothesis import given, settings, strategies as st

from engine.evaluar import evaluar
from engine.modelos import Movimiento
from engine.reglas_io import cargar_contexto_base, cargar_reglas
from tests.test_motor import ficha

HOY = date(2026, 10, 17)
CTX, REGLAS = cargar_contexto_base(HOY), cargar_reglas(HOY)[0]

VIOLACIONES = {
    "duplicada": dict(beneficiario="Papelería Corporativa Anáhuac S.A. de C.V.", numero="TA-0931", monto="12500", moneda="MXN",
                      vence="2026-09-25", cuenta_original="Cuenta demo ···0029"),
    "beneficiario_nuevo": dict(beneficiario="Desconocido SAS"),
    "cuenta_distinta": dict(cuenta_aclarada="Banco Falso ···0000"),
    "lecturas_distintas": dict(segunda_lectura="no_coincide"),
    "lectura_dudosa": dict(lectura_ia="dudosa"),
    "orden_en_texto": dict(orden_en_texto=True),
    "monto_aclarado": dict(valores_aclarados={"monto": "1"}),
    "sin_tasa": dict(moneda="JPY"),
    "supera_acuerdo": dict(monto="3000000"),
    "supera_techo": dict(beneficiario="Inversiones Metalmecánicos Cauca S.A.S.", monto="70000000", cuenta_original="Cuenta demo ···0053"),
    "inesperada": dict(recibida="2026-10-12"),
    "segunda_lectura_no_disponible": dict(segunda_lectura="no_disponible"),     # R2.2
    "numero_solo_aclarado": dict(origen_campos={"numero": "aclarado"}),         # R2.5
    "vence_solo_aclarado": dict(origen_campos={"vence": "aclarado"}),           # R2.5
    "monto_aclarado_sin_respaldo": dict(monto="2600000", origen_campos={"monto": "aclarado"}),
}


@settings(max_examples=300, deadline=None)
@given(st.sampled_from(sorted(VIOLACIONES)), st.sampled_from(["ok", "dudosa"]), st.booleans())
def test_nunca_paga_si_viola_una_regla(violacion, lectura, orden):
    cambios = {"lectura_ia": lectura, "orden_en_texto": orden, **VIOLACIONES[violacion]}
    r = evaluar(ficha(**cambios), CTX, REGLAS)
    assert r.decision != "PAGAR", (violacion, r.motivo)


@settings(max_examples=300, deadline=None)
@given(st.dictionaries(st.sampled_from(["monto", "moneda", "beneficiario", "numero", "vence", "recibida",
                                         "lectura_ia", "segunda_lectura", "cuenta_aclarada"]),
                       st.one_of(st.text(max_size=12), st.integers(-5, 10**8), st.none()), max_size=6),
       st.sampled_from([0, 1, 2]))
def test_ficha_cualquiera_nunca_rompe_ni_paga_sin_cumplir(cambios, _):
    r = evaluar(ficha(**cambios), CTX, REGLAS)       # nunca lanza
    if r.decision == "PAGAR":
        assert all(x.resultado == "OK" for x in r.revisiones) and r.nivel == "NINGUNO"


@settings(max_examples=200, deadline=None)
@given(st.integers(0, 10**8), st.sampled_from(["PAGADA", "PENDIENTE", "FRENADA", "RECHAZADA"]))
def test_pagar_nunca_supera_el_autopago_ni_el_presupuesto(previo, estado):
    mov = Movimiento(factura_id="H", beneficiario="Tecnología Cafetera S.A.S.", numero="H", monto=previo, moneda="COP",
                     vence=date(2026, 10, 1), monto_base=previo, estado=estado, periodo="2026-10")
    ctx = CTX.model_copy(update={"historial": CTX.historial + [mov]})
    r = evaluar(ficha(), ctx, REGLAS)
    if r.decision == "PAGAR":
        acumulado = previo if estado in ("PAGADA", "PENDIENTE") else 0
        assert acumulado + 2400000 <= REGLAS.autopago_max
