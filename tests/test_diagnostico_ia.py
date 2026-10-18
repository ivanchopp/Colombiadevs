"""Spec extraccion-y-agente-de-entrada EA2b.10 y EA2b.11 (R6): ver por qué la IA no lee, sin abrir los Logs."""
from pathlib import Path
from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest

from agents import flujo, lectura_ia
from agents.lectura_ia import LecturaFallida, leer_con_ia
from tests.test_agente_entrada import ClienteFalso, GeminiFalso as GeminiLectura, LEIDO, sin_clave  # noqa: F401 (fixture autouse)

CLAVE = "AIzaSyUnaClaveMuyLargaYSecreta1234567890"
LECTURA = dict(beneficiario="Prueba SAS", numero="T-1", monto="100", moneda="COP", vence="2026-10-30", cuenta=None, dudosos=[])
RUTA = str(Path(__file__).resolve().parent.parent / "app" / "Panel_1_Proveedor.py")


@pytest.fixture(autouse=True)
def limpia():
    lectura_ia.ULTIMA_FALLA.update(cuando=None, proveedor=None, mensaje=None)


class GeminiFalso:
    """Imita client.models.list de google-genai (sin messages: se reconoce como Gemini)."""

    def __init__(self, nombres, falla=False):
        self.nombres, self.falla = nombres, falla
        self.models = SimpleNamespace(list=self._listar)

    def _listar(self):
        if self.falla:
            raise RuntimeError("403 sin permiso")
        return [SimpleNamespace(name=n, supported_actions=a) for n, a in self.nombres]


def test_ea2b_10_una_falla_de_lectura_queda_a_la_vista(almacen, sala, monkeypatch):
    monkeypatch.setenv("FACTURAS_MAX", "20")
    flujo.recibir(almacen, sala, "f.txt", b"Total: 5 COP", cliente=ClienteFalso({}, falla=True))
    f = lectura_ia.ULTIMA_FALLA
    assert f["cuando"] and f["proveedor"] and "sin red" in f["mensaje"]


def test_ea2b_10_la_falla_guardada_nunca_lleva_el_valor_de_la_clave(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", CLAVE)
    lectura_ia.registrar_falla(RuntimeError(f"400 API key not valid: {CLAVE}"))
    assert CLAVE not in lectura_ia.ULTIMA_FALLA["mensaje"] and "***" in lectura_ia.ULTIMA_FALLA["mensaje"]


def test_ea2b_10_una_lectura_buena_no_registra_falla(almacen, sala):
    flujo.recibir(almacen, sala, "f.txt", b"Total: 5 COP", cliente=ClienteFalso(LECTURA))
    assert lectura_ia.ULTIMA_FALLA["cuando"] is None


# --- EA2b.11: probar la conexión -------------------------------------------------------------
def test_ea2b_11_sin_proveedor_lo_dice():
    r = lectura_ia.probar_conexion()
    assert not r["ok"] and r["proveedor"] is None and "No hay proveedor" in r["detalle"]


def test_ea2b_11_si_la_ia_lee_bien_la_factura_de_prueba_dice_ok():
    c = ClienteFalso(LECTURA)
    r = lectura_ia.probar_conexion(c)
    assert r["ok"] and r["proveedor"] == "claude" and len(c.llamadas) == 2       # un texto y un PDF (EA2b.12)


def test_ea2b_11_si_la_ia_lee_otra_cosa_no_dice_ok():
    r = lectura_ia.probar_conexion(ClienteFalso({**LECTURA, "monto": "999"}))
    assert not r["ok"] and "otra cosa" in r["detalle"]


def test_ea2b_11_si_falla_muestra_el_error_sin_la_clave(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", CLAVE)
    r = lectura_ia.probar_conexion(ClienteFalso({}, falla=True))
    assert not r["ok"] and "sin red" in r["detalle"]
    cliente = GeminiFalso([])
    cliente.models.generate_content = lambda **kw: (_ for _ in ()).throw(RuntimeError(f"404 models/x not found {CLAVE}"))
    r = lectura_ia.probar_conexion(cliente, "gemini")
    assert not r["ok"] and "404" in r["detalle"] and CLAVE not in r["detalle"]


def test_ea2b_11_para_gemini_lista_los_modelos_para_elegir():
    c = GeminiFalso([("models/gemini-3-flash", ["generateContent"]), ("models/gemini-2.5-pro", ["generateContent"]),
                     ("models/embedding-001", ["embedContent"]), ("models/text-bison", ["generateContent"])])
    assert lectura_ia.modelos_disponibles(c) == ["gemini-2.5-pro", "gemini-3-flash"]     # sin embeddings ni otras marcas


def test_ea2b_11_si_no_se_puede_listar_la_lista_queda_vacia_y_no_rompe():
    assert lectura_ia.modelos_disponibles(GeminiFalso([], falla=True)) == []
    assert lectura_ia.modelos_disponibles(ClienteFalso({})) == []                          # Claude: no aplica


# --- La pantalla -------------------------------------------------------------------------------
def abrir(tmp_path, monkeypatch, diagnostico=True, clave=True):
    monkeypatch.setenv("ACTA_DB", str(tmp_path / "p.db"))
    if clave:
        monkeypatch.setenv("GEMINI_API_KEY", CLAVE)
    else:
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    at = AppTest.from_file(RUTA, default_timeout=30)
    if diagnostico:
        at.query_params["diagnostico"] = "1"
    return at.run()


def textos(at):
    return " ".join(x.value for x in at.text)


def test_ea2b_11_el_boton_solo_aparece_con_el_parametro_y_con_proveedor(tmp_path, monkeypatch):
    sin_param = abrir(tmp_path, monkeypatch, diagnostico=False)
    assert "Probar la conexión con la IA ahora" not in [b.label for b in sin_param.button]
    sin_clave_ = abrir(tmp_path, monkeypatch, clave=False)
    assert "Probar la conexión con la IA ahora" not in [b.label for b in sin_clave_.button]
    con = abrir(tmp_path, monkeypatch)
    assert "Probar la conexión con la IA ahora" in [b.label for b in con.button]


def test_ea2b_10_el_diagnostico_muestra_la_ultima_falla(tmp_path, monkeypatch):
    assert "ninguna desde el último arranque" in textos(abrir(tmp_path, monkeypatch))
    lectura_ia.registrar_falla(RuntimeError("404 NOT_FOUND modelo retirado"))
    t = textos(abrir(tmp_path, monkeypatch))
    assert "Última falla de lectura con IA:" in t and "404 NOT_FOUND modelo retirado" in t and CLAVE not in t


def test_ea2b_11_al_pulsar_el_boton_se_ve_el_resultado_sin_la_clave(tmp_path, monkeypatch):
    monkeypatch.setattr(lectura_ia, "probar_conexion", lambda *a, **k: {
        "ok": False, "proveedor": "gemini", "modelo": "gemini-2.5-flash",
        "detalle": "404 NOT_FOUND: el modelo ya no existe", "modelos": ["gemini-3-flash", "gemini-3-pro"]})
    at = abrir(tmp_path, monkeypatch)
    next(b for b in at.button if b.label == "Probar la conexión con la IA ahora").click().run()
    t = textos(at)
    assert not at.exception and "FALLA · gemini (gemini-2.5-flash)" in t and "404 NOT_FOUND" in t
    assert "Modelos disponibles: gemini-3-flash, gemini-3-pro" in t and CLAVE not in t


# --- EA2b.12: la prueba también lee un PDF ----------------------------------------------------
def test_ea2b_12_la_prueba_envia_un_pdf_real_a_la_ia():
    c = ClienteFalso(LECTURA)
    lectura_ia.probar_conexion(c)
    bloques = [b for ll in c.llamadas for m in ll["messages"] for b in m["content"] if b["type"] == "document"]
    assert len(bloques) == 1 and bloques[0]["source"]["media_type"] == "application/pdf"
    pdf = lectura_ia.base64.b64decode(bloques[0]["source"]["data"])
    from agents import archivo
    assert archivo.detectar_tipo(pdf) == "pdf" and "Total: 100 COP" in archivo.extraer_texto("pdf", pdf)


def test_ea2b_12_si_solo_falla_el_pdf_no_dice_ok_y_lo_separa():
    c = ClienteFalso(LECTURA)
    original = c.messages.create

    def create(**kw):
        if any(b["type"] == "document" for m in kw["messages"] for b in m["content"]):
            raise RuntimeError("400 el archivo no se pudo procesar")
        return original(**kw)
    c.messages.create = create
    r = lectura_ia.probar_conexion(c)
    assert not r["ok"] and "Texto: leyó bien" in r["detalle"] and "PDF: FALLA" in r["detalle"]


def test_ea2b_12_gemini_cortado_dice_el_motivo_de_fin():
    g = GeminiLectura(LEIDO)
    g.models.generate_content = lambda **kw: SimpleNamespace(
        text='{"beneficiario": "Prue', candidates=[SimpleNamespace(finish_reason=SimpleNamespace(name="MAX_TOKENS"))])
    with pytest.raises(LecturaFallida, match="MAX_TOKENS"):
        leer_con_ia("pdf", b"%PDF-1.4 x", None, g)


def test_ea2b_12_el_tope_de_salida_de_gemini_es_holgado():
    g = GeminiLectura(LEIDO)
    leer_con_ia("pdf", b"%PDF-1.4 x", None, g)
    assert g.llamadas[0]["config"].max_output_tokens >= 16384


# --- PP2.6: el selector de archivos se vacía al enviar ----------------------------------------
def test_pp2_6_el_selector_de_archivos_cambia_de_clave_tras_cada_envio(tmp_path, monkeypatch):
    monkeypatch.setenv("ACTA_DB", str(tmp_path / "p.db"))
    at = AppTest.from_file(RUTA, default_timeout=30)
    at.session_state["envio"] = 2
    at.run()
    assert not at.exception
    assert at.get("file_uploader")[0].proto.id and "archivo_2" in at.get("file_uploader")[0].key
    fuente = Path(RUTA).read_text(encoding="utf-8")
    assert fuente.count('st.session_state["envio"]') == 1 and "archivo_{st.session_state.get('envio', 0)}" in fuente
