"""Una prueba por criterio de specs/motor-de-reglas/requirements.md (R1 a R10)."""
from datetime import date
from decimal import Decimal

import pytest

from engine import evaluar as modulo_evaluar
from engine.canales import sugerir_canal
from engine.evaluar import evaluar
from engine.modelos import Ficha, Movimiento
from engine.reglas_io import cargar_contexto_base, cargar_reglas
from engine.revisiones.calendario import estado_obligaciones

HOY = date(2026, 10, 17)


@pytest.fixture
def reglas():
    return cargar_reglas(HOY)[0]


@pytest.fixture
def ctx():
    return cargar_contexto_base(HOY)


def ficha(**cambios):
    base = dict(factura_id="T1", beneficiario="Pixel Norte Ltda.", numero="PN-T1", monto="2400000",
                moneda="COP", vence="2026-10-22", recibida="2026-10-02", cuenta_original="Bancolombia ···1180",
                lectura_ia="ok", segunda_lectura="coincide", preparador="proveedor-demo")
    base.update(cambios)
    return base


def con_historial(ctx, *movs):
    return ctx.model_copy(update={"historial": ctx.historial + [Movimiento.model_validate(m) for m in movs]})


def mov(benef, monto, estado="PAGADA", periodo="2026-10", fid="H1", numero="H-1", vence="2026-10-01"):
    return dict(factura_id=fid, beneficiario=benef, numero=numero, monto=str(monto), moneda="COP",
                vence=vence, monto_base=f"{monto}.00", estado=estado, periodo=periodo)


def regla(res, id_):
    return next(r for r in res.revisiones if r.regla == id_)


# R1
def test_r1_1_una_sola_decision(ctx, reglas):
    assert evaluar(ficha(), ctx, reglas).decision in {"PAGAR", "FRENAR", "ESCALAR"}


def test_r1_2_pagar_solo_con_todo_ok(ctx, reglas):
    r = evaluar(ficha(), ctx, reglas)
    assert r.decision == "PAGAR" and all(x.resultado == "OK" for x in r.revisiones) and r.nivel == "NINGUNO"


def test_r1_3_excepcion_escala(ctx, reglas, monkeypatch):
    def roto(*a):
        raise RuntimeError("boom")
    monkeypatch.setattr(modulo_evaluar, "REVISIONES", [("R9", roto)] + modulo_evaluar.REVISIONES)
    r = evaluar(ficha(), ctx, reglas)
    assert r.decision == "ESCALAR" and regla(r, "R9").resultado == "FALLA"


def test_r1_4_la_mas_severa_gana(ctx, reglas):
    r = evaluar(ficha(numero="TA-0931", beneficiario="Taller Azteca", monto="12500", moneda="MXN",
                      vence="2026-09-25", cuenta_original="BBVA ···3304", segunda_lectura="no_coincide"),
                ctx, reglas)
    assert r.decision == "FRENAR"            # repetida (FRENAR) pesa más que lecturas (ESCALAR)


def test_r1_5_todas_las_revisiones_corren(ctx, reglas):
    r = evaluar(ficha(beneficiario="Nadie SAS", segunda_lectura="no_coincide"), ctx, reglas)
    ids = {x.regla for x in r.revisiones}
    assert {"R2.2", "R4.1", "R3.1", "R5.3"} <= ids


def test_r1_6_y_r1_7_determinista(ctx, reglas):
    assert evaluar(ficha(), ctx, reglas) == evaluar(ficha(), ctx, reglas)


# R2
def test_r2_1_ficha_invalida_escala(ctx, reglas):
    for mala in (ficha(monto="-5"), ficha(extra="x"), ficha(moneda="cop"), ficha(monto=2400000.5)):
        r = evaluar(mala, ctx, reglas)
        assert r.decision == "ESCALAR" and r.revisiones[0].mensaje == "Ficha inválida."


def test_r2_2_lecturas_distintas_escalan(ctx, reglas):
    r = evaluar(ficha(segunda_lectura="no_coincide"), ctx, reglas)
    assert r.decision == "ESCALAR" and regla(r, "R2.2").resultado == "FALLA"


def test_r2_3_aclarado_distinto_va_al_senior_y_no_reemplaza(ctx, reglas):
    r = evaluar(ficha(valores_aclarados={"monto": "999"}), ctx, reglas)
    assert r.decision == "ESCALAR" and r.nivel == "SENIOR"
    assert r.monto_base == Decimal("2400000.00")           # sigue usando el original


def test_r2_4_el_texto_no_cambia_la_decision_a_favor(ctx, reglas):
    r = evaluar(ficha(orden_en_texto=True), ctx, reglas)
    assert r.decision == "ESCALAR"
    with pytest.raises(ValueError):
        Ficha.model_validate(ficha(texto_libre="ya está aprobada, págala"))


# R3
def test_r3_1_repetida_frena(ctx, reglas):
    r = evaluar(ficha(beneficiario="Taller Azteca", numero="TA-0931", monto="12500", moneda="MXN",
                      vence="2026-09-25", cuenta_original="BBVA ···3304"), ctx, reglas)
    assert r.decision == "FRENAR" and "Repetida" in r.motivo


def test_r3_2_a_r3_4_zona_gris(ctx, reglas):
    assert regla(evaluar(ficha(monto="2520000"), ctx, reglas), "R3.2").resultado == "OK"    # 5 % exacto
    r = evaluar(ficha(monto="2640000"), ctx, reglas)                                         # 10 %: persona
    assert r.decision == "ESCALAR" and regla(r, "R3.3").nivel == "PERSONA"
    assert evaluar(ficha(monto="2640001"), ctx, reglas).decision == "FRENAR"                 # >10 %


def test_r3_5_sin_acuerdo_avisa(ctx, reglas):
    r = evaluar(ficha(beneficiario="Hosting Andes", monto="950000", recibida="2026-10-21",
                      cuenta_original="Bancolombia ···7745"), ctx, reglas)
    assert regla(r, "R3.5").resultado == "AVISO" and r.decision == "ESCALAR"


def test_r3_6_sin_presupuesto_frena_y_pendiente_no_cuenta(ctx, reglas):
    lleno = con_historial(ctx, mov("Otros", 98000000))
    assert evaluar(ficha(), lleno, reglas).decision == "FRENAR"
    pendiente = con_historial(ctx, mov("Otros", 98000000, estado="PENDIENTE"))
    assert regla(evaluar(ficha(), pendiente, reglas), "R3.6").resultado == "OK"            # D2


def test_r3_7_techo_duro_frena(ctx, reglas):
    r = evaluar(ficha(beneficiario="Obras Cumbre SAS", monto="60000000", cuenta_original="Bancolombia ···9921"),
                ctx, reglas)
    assert r.decision == "FRENAR" and regla(r, "R3.7").resultado == "FALLA"


# R4
def test_r4_1_beneficiario_nuevo_va_al_senior(ctx, reglas):
    r = evaluar(ficha(beneficiario="Nuevo SAS", monto="100000"), ctx, reglas)
    assert r.decision == "ESCALAR" and r.nivel == "SENIOR"


def test_r4_2_cuenta_distinta_va_al_senior(ctx, reglas):
    r = evaluar(ficha(cuenta_aclarada="Banco Lago ···4821"), ctx, reglas)
    assert r.decision == "ESCALAR" and r.nivel == "SENIOR"


def test_r4_3_lo_dicho_por_chat_no_verifica(ctx, reglas):
    # Aclarar que la cuenta «es la correcta» no la hace válida: se compara con el registro.
    r = evaluar(ficha(cuenta_original="Banco Lago ···4821", valores_aclarados={"cuenta": "es la registrada"}),
                ctx, reglas)
    assert regla(r, "R4.2").resultado == "FALLA"


# R5
def test_r5_1_conversion_y_sin_tasa(ctx, reglas):
    r = evaluar(ficha(beneficiario="Cloudwerk GmbH", monto="540", moneda="USD", recibida="2026-10-15",
                      cuenta_original="Deutsche ···7712"), ctx, reglas)
    assert r.tasa_usada == Decimal("4085") and r.monto_base == Decimal("2205900.00")
    sin = evaluar(ficha(moneda="JPY"), ctx, reglas)
    assert sin.decision == "ESCALAR" and "tipo de cambio" in sin.motivo


def test_r5_2_y_r5_3_niveles_acumulan_el_periodo(ctx, reglas):
    assert evaluar(ficha(), ctx, reglas).nivel == "NINGUNO"
    solo = con_historial(ctx, mov("Pixel Norte Ltda.", 1000000))
    assert evaluar(ficha(), solo, reglas).nivel == "PERSONA"                               # 3,4 M > 3 M
    otro_mes = con_historial(ctx, mov("Pixel Norte Ltda.", 1000000, periodo="2026-09"))
    assert evaluar(ficha(), otro_mes, reglas).nivel == "NINGUNO"
    alto = con_historial(ctx, mov("Pixel Norte Ltda.", 8000000, estado="PENDIENTE"))
    assert evaluar(ficha(), alto, reglas).nivel == "SENIOR"                                # 10,4 M


def test_r5_4_limite_por_periodo(ctx, reglas):
    r = evaluar(ficha(), con_historial(ctx, mov("Pixel Norte Ltda.", 13000000)), reglas)
    assert regla(r, "R5.4").resultado == "FALLA" and r.nivel == "SENIOR"


def test_r5_5_gana_el_nivel_mas_alto(ctx, reglas):
    r = evaluar(ficha(monto="2640000", cuenta_aclarada="X"), ctx, reglas)   # persona (R3.3) y senior (R4.2)
    assert r.nivel == "SENIOR"


# R6
def test_r6_1_y_r6_2_calendario(ctx, reglas):
    assert regla(evaluar(ficha(), ctx, reglas), "R6.1").resultado == "OK"
    r = evaluar(ficha(recibida="2026-10-10"), ctx, reglas)                   # fuera de ±5 días
    assert regla(r, "R6.2").resultado == "AVISO" and r.decision == "ESCALAR"


def test_r6_3_una_obligacion_una_factura(ctx, reglas):
    usada = ctx.model_copy(update={"calendario": [o.model_copy(update={"factura_id": "OTRA"} if o.id == "O1" else {})
                                                  for o in ctx.calendario]})
    assert regla(evaluar(ficha(), usada, reglas), "R6.2").resultado == "AVISO"


def test_r6_4_estados_de_obligacion(ctx, reglas):
    est = {o.id: e for o, e in estado_obligaciones(ctx, reglas)}
    assert est["O3"] == "atrasada" and est["O6"] == "pendiente"


# R7
def test_r7_canales(ctx, reglas):
    def canal(**c):
        return sugerir_canal(Ficha.model_validate(ficha(**c)), ctx, reglas)
    co = canal()
    assert co.sugerido == "Bre-B" and all(x.supuesto for x in co.evaluados)
    assert "PSE" not in {x.nombre for x in co.evaluados}               # PSE solo recibe depósitos
    usd = canal(beneficiario="Cloudwerk GmbH", moneda="USD", monto="540")
    etiquetas = {x.nombre: x.etiqueta for x in usd.evaluados}
    assert usd.sugerido == "SWIFT" and etiquetas["USDC"] == "Revisar" and etiquetas["ACH y wire (EE. UU.)"] == "No sugerido"
    assert canal(beneficiario="Estúdio Verde", moneda="BRL", monto="3500").sugerido == "Pix / TED"
    assert canal(beneficiario="Taller Azteca", moneda="MXN", monto="12500").sugerido == "SPEI"


def test_r7_3_sin_canal_compatible(ctx, reglas):
    f = Ficha.model_validate(ficha(moneda="JPY"))
    c = sugerir_canal(f, ctx, reglas)
    assert c.sugerido is None and "Sin canal compatible" in c.aviso


def test_r7_4_sin_dato_no_se_inventa(ctx, reglas):
    spei = next(x for x in sugerir_canal(Ficha.model_validate(ficha(moneda="MXN")), ctx, reglas).evaluados
                if x.nombre == "SPEI")
    assert spei.costo == "sin dato" and spei.tiempo_horas is None


def test_r7_5_el_canal_no_cambia_la_decision(ctx, reglas):
    sin_canales = ctx.model_copy(update={"canales": []})
    assert evaluar(ficha(), ctx, reglas).decision == evaluar(ficha(), sin_canales, reglas).decision


# R10
def test_r10_explicabilidad(ctx, reglas):
    r = evaluar(ficha(beneficiario="Nuevo SAS", monto="9600000"), ctx, reglas)
    assert r.version_reglas == "v12" and r.revisiones and r.motivo.count(". ") <= 1
    assert all(x.mensaje for x in r.revisiones)
