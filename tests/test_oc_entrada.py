"""Spec ordenes-de-compra, OC3 (OT5): el agente de entrada lee la orden de compra y el NIT de la factura."""
import pytest

from acta.estado import facturas_por_estado
from agents import ejemplos, flujo, segunda_lectura
from agents.lectura_ia import ESQUEMA, OPCIONALES, leer_con_ia
from tests.test_agente_entrada import ClienteFalso, decision, sin_clave  # noqa: F401 (sin_clave: fixture autouse)

BASE = dict(beneficiario="X SAS", numero="N-1", monto="100", moneda="COP", vence="2026-10-30", cuenta=None, dudosos=[])


@pytest.fixture(autouse=True)
def hoy(monkeypatch):
    monkeypatch.setenv("FECHA_DEMO", "2026-10-17")
    monkeypatch.setenv("FACTURAS_MAX", "20")


# --- OC3.1: lectura con IA ---------------------------------------------------------------------
def test_oc3_1_el_esquema_pide_los_dos_campos_y_no_los_vuelve_dudosos():
    assert set(OPCIONALES) <= set(ESQUEMA["properties"]) and set(OPCIONALES) <= set(ESQUEMA["required"])
    assert not set(OPCIONALES) & set(ESQUEMA["properties"]["dudosos"]["items"]["enum"])


def test_oc3_1_la_ia_devuelve_la_oc_y_la_identificacion_tal_como_estan_escritas():
    r = leer_con_ia("txt", b"", "x", ClienteFalso({**BASE, "orden_compra": " PO-2026-001 ", "id_tributaria": "999016272-1"}))
    assert r["orden_compra"] == "PO-2026-001" and r["id_tributaria"] == "999016272-1"


def test_oc3_1_si_no_aparecen_quedan_vacios_y_nunca_se_estiman():
    r = leer_con_ia("txt", b"", "x", ClienteFalso(BASE))
    assert r["orden_compra"] is None and r["id_tributaria"] is None and r["dudosos"] == []


def test_oc3_1_los_valores_absurdos_se_recortan():
    r = leer_con_ia("txt", b"", "x", ClienteFalso({**BASE, "orden_compra": "P" * 500, "id_tributaria": "9" * 500}))
    assert len(r["orden_compra"]) <= 40 and len(r["id_tributaria"]) <= 20


# --- OC3.2: segunda lectura --------------------------------------------------------------------
@pytest.mark.parametrize("texto,oc", [
    ("Orden de compra: PO-2026-001", "PO-2026-001"), ("ORDEN DE COMPRA No. po 2026 001", "PO 2026 001"),
    ("O.C. No. 4500012345", "4500012345"), ("Purchase order # PO-77-12", "PO-77-12"),
])
def test_oc3_2_los_patrones_reconocen_la_orden_de_compra(texto, oc):
    assert segunda_lectura.leer(texto)["orden_compra"] == oc


@pytest.mark.parametrize("texto,ident", [
    ("NIT: 999016272-1", "999016272-1"), ("RUC 20123456789", "20123456789"), ("RFC: ABC010203XY9", "ABC010203XY9"),
])
def test_oc3_2_los_patrones_reconocen_la_identificacion_tributaria(texto, ident):
    assert segunda_lectura.leer(texto)["id_tributaria"] == ident


@pytest.mark.parametrize("texto", ["Recibo de compra 2026-10-14", "Orden de compra: pendiente", "NIT 123", "Total: 5 COP"])
def test_oc3_2_no_inventan_lo_que_no_hay(texto):
    r = segunda_lectura.leer(texto)
    assert r["orden_compra"] is None and r["id_tributaria"] is None


TEXTO = "Proveedor: X SAS\nVence: 2026-10-30\nTotal: 100 COP\nOrden de compra: PO-2026-001\nNIT: 999016272-1\n"
IA = dict(beneficiario="X SAS", monto="100", moneda="COP", vence="2026-10-30")


def test_oc3_2_coincide_cuando_ambas_lecturas_ven_lo_mismo_aunque_cambie_el_formato():
    ia = {**IA, "orden_compra": "po2026001", "id_tributaria": "999016272-1"}
    assert segunda_lectura.comparar(ia, TEXTO) == ("coincide", [])


@pytest.mark.parametrize("cambios,campo", [
    ({"orden_compra": "PO-2026-002", "id_tributaria": "999016272-1"}, "orden_compra"),     # la IA vio otra OC
    ({"orden_compra": None, "id_tributaria": "999016272-1"}, "orden_compra"),              # la IA no la vio
    ({"orden_compra": "PO-2026-001", "id_tributaria": "999016272-9"}, "id_tributaria"),    # otro NIT
    ({"orden_compra": "PO-2026-001", "id_tributaria": None}, "id_tributaria"),
])
def test_oc3_2_si_difieren_no_coincide_y_se_escala(cambios, campo):
    res, difieren = segunda_lectura.comparar({**IA, **cambios}, TEXTO)
    assert res == "no_coincide" and campo in difieren


def test_oc3_2_la_ia_que_inventa_una_oc_que_el_texto_no_tiene_no_coincide():
    res, difieren = segunda_lectura.comparar({**IA, "orden_compra": "PO-2026-001", "id_tributaria": None},
                                             "Proveedor: X SAS\nVence: 2026-10-30\nTotal: 100 COP\n")
    assert res == "no_coincide" and difieren == ["orden_compra"]


def test_oc3_2_una_factura_sin_oc_se_compara_como_siempre():
    texto = "Proveedor: X SAS\nVence: 2026-10-30\nTotal: 100 COP\n"
    assert segunda_lectura.comparar({**IA, "orden_compra": None, "id_tributaria": None}, texto) == ("coincide", [])


# --- De punta a punta: archivo → ficha → motor → acta -------------------------------------------
def subir(almacen, sala, clave, lectura=None):
    nombre, datos = ejemplos.leer_ejemplo(clave)
    cliente = ClienteFalso(lectura or ejemplos.LECTURAS_GUARDADAS[clave])
    e = flujo.recibir(almacen, sala, nombre, datos, cliente=cliente)
    return e, decision(almacen, sala, e["factura_id"])


def test_oc3_1_la_ficha_lleva_la_oc_y_el_nit_que_trae_la_factura(almacen, sala):
    e, d = subir(almacen, sala, "oc_cuadra")
    assert e["modo"] == "ia" and e["segunda"] == "coincide"
    assert d["ficha"]["orden_compra"] == "PO-2026-001" and d["ficha"]["id_tributaria"] == "999016272-1"


def test_oc_una_oc_que_cuadra_y_estaba_en_el_calendario_se_paga_sola(almacen, sala):
    _, d = subir(almacen, sala, "oc_cuadra")
    assert (d["decision"], d["nivel"]) == ("PAGAR", "NINGUNO")
    assert any(r["regla"] == "OC4.1" and r["resultado"] == "OK" for r in d["revisiones"])


def test_oc_un_monto_alterado_se_frena(almacen, sala):
    _, d = subir(almacen, sala, "oc_monto")
    assert d["decision"] == "FRENAR" and "orden de compra" in d["motivo"]


def test_oc_un_nit_distinto_va_al_senior(almacen, sala):
    _, d = subir(almacen, sala, "oc_nit")
    assert (d["decision"], d["nivel"]) == ("ESCALAR", "SENIOR")


def test_oc_la_misma_oc_en_una_segunda_factura_se_frena(almacen, sala):
    subir(almacen, sala, "oc_cuadra")
    lectura = {**ejemplos.LECTURAS_GUARDADAS["oc_cuadra"], "numero": "AH-4499"}
    nombre, datos = ejemplos.leer_ejemplo("oc_cuadra")
    datos = datos.replace(b"AH-4410", b"AH-4499")
    e = flujo.recibir(almacen, sala, nombre, datos, cliente=ClienteFalso(lectura))
    d = decision(almacen, sala, e["factura_id"])
    assert d["decision"] == "FRENAR" and any(r["regla"] == "OC4.6" for r in d["revisiones"])


def test_oc3_3_el_proveedor_no_se_entera_de_la_oc_ni_de_su_estado(almacen, sala):
    for clave in ("oc_cuadra", "oc_monto", "oc_nit"):
        e, _ = subir(almacen, sala, clave)
        dicho = " ".join(t for _, t in e["chat"]).lower()
        for prohibido in ("po-2026", "orden de compra", "nit", "monto autorizado", "ya facturada", "inexistente"):
            assert prohibido not in dicho, (clave, prohibido)
        assert flujo.estado_para_proveedor(almacen, sala, e) in {"resuelta", "en revisión"}


def test_oc3_3_el_agente_no_recibe_las_ordenes_ni_los_proveedores(almacen, sala):
    nombre, datos = ejemplos.leer_ejemplo("oc_cuadra")
    cliente = ClienteFalso(ejemplos.LECTURAS_GUARDADAS["oc_cuadra"])
    flujo.recibir(almacen, sala, nombre, datos, cliente=cliente)
    enviado = str(cliente.llamadas)
    for secreto in ("PO-2026-005", "PO-2026-010", "Cuenta demo ···0010", "929610444-4", "autopago", "ordenes_compra"):
        assert secreto not in enviado


def test_oc_sin_ia_una_factura_con_oc_nunca_se_paga(almacen, sala):
    for clave in ("oc_cuadra", "oc_monto", "oc_nit"):
        nombre, datos = ejemplos.leer_ejemplo(clave)
        e = flujo.recibir(almacen, sala, nombre, datos)
        d = decision(almacen, sala, e["factura_id"])
        assert e["modo"] == "regex" and d["decision"] != "PAGAR", clave
        assert d["ficha"]["orden_compra"] is not None               # los patrones sí la leyeron


def test_oc_el_motor_sigue_sin_poder_pagar_si_la_ia_inventa_la_oc(almacen, sala):
    """La IA dice que hay una OC que el texto no trae: la segunda lectura no coincide y se escala."""
    lectura = {**ejemplos.LECTURAS_GUARDADAS["normal"], "orden_compra": "PO-2026-001", "id_tributaria": "999016272-1"}
    nombre, datos = ejemplos.leer_ejemplo("normal")
    e = flujo.recibir(almacen, sala, nombre, datos, cliente=ClienteFalso(lectura))
    d = decision(almacen, sala, e["factura_id"])
    assert e["segunda"] == "no_coincide" and d["decision"] == "ESCALAR"
