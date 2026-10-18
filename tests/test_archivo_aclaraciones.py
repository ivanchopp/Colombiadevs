"""Pruebas de función que cierran huecos de cobertura: validación de archivos (EA1) y de respuestas del chat (EA5)."""
import pytest
from hypothesis import given, settings, strategies as st

from agents import aclaraciones, archivo
from agents.archivo import ArchivoRechazado

EML = (b"From: Proveedor <p@example.com>\nSubject: Factura IS-1\nContent-Type: text/plain; charset=utf-8\n\n"
       b"Total: 100 USD\n")


# --- archivo.validar -------------------------------------------------------------------------------------
@pytest.mark.parametrize("nombre,datos,mensaje", [
    ("a.txt", b"", "vacío"),
    ("a.txt", b"x" * (archivo.TAMANO_MAX + 1), "5 MB"),
    ("a.exe", b"Total: 1 COP", "Solo se aceptan"),
    ("a", b"Total: 1 COP", "Solo se aceptan"),
    ("a.pdf", b"Total: 1 COP", "no coincide"),
    ("a.png", b"%PDF-1.4 x", "no coincide"),
    ("a.txt", b"abc\x00def", "No reconozco"),
    ("a.txt", b"\xff\xfe\x00\x01 binario", "No reconozco"),
])
def test_ea1_se_rechaza_lo_que_no_es_una_factura_valida(nombre, datos, mensaje):
    with pytest.raises(ArchivoRechazado, match=mensaje):
        archivo.validar(nombre, datos)


@pytest.mark.parametrize("nombre,datos,tipo", [
    ("a.pdf", b"%PDF-1.4 x", "pdf"), ("a.png", b"\x89PNG\r\n\x1a\n0", "imagen"), ("a.jpg", b"\xff\xd8\xff\xe0 x", "imagen"),
    ("a.txt", "Total: 5 COP ñ".encode(), "txt"), ("a.eml", EML, "eml"), ("a.txt", EML, "eml"),
    ("a.xml", b'<?xml version="1.0" encoding="ISO-8859-1"?><DTE><x>\xf1</x></DTE>', "xml"),   # EA12.8: no es UTF-8
])
def test_ea1_el_tipo_sale_del_contenido_y_no_del_nombre(nombre, datos, tipo):
    assert archivo.validar(nombre, datos) == tipo


# --- archivo.extraer_texto ---------------------------------------------------------------------------------
def test_ea3_un_correo_se_lee_con_remitente_asunto_y_cuerpo():
    t = archivo.extraer_texto("eml", EML)
    assert "De: Proveedor <p@example.com>" in t and "Asunto: Factura IS-1" in t and "Total: 100 USD" in t


def test_ea3_un_pdf_roto_o_una_imagen_no_dan_texto_ni_fallan():
    assert archivo.extraer_texto("pdf", b"%PDF-1.4 esto no es un pdf") is None
    assert archivo.extraer_texto("imagen", b"\x89PNG\r\n\x1a\n0") is None


def test_ea12_8_un_xml_con_codificacion_desconocida_se_lee_como_utf8_sin_fallar():
    datos = b'<?xml version="1.0" encoding="codificacion-inventada"?><DTE>texto</DTE>'
    assert "texto" in archivo.extraer_texto("xml", datos)


def test_ea12_8_un_xml_latin1_conserva_sus_tildes():
    datos = '<?xml version="1.0" encoding="ISO-8859-1"?><DTE>Compañía</DTE>'.encode("latin-1")
    assert "Compañía" in archivo.extraer_texto("xml", datos)


@settings(max_examples=200, deadline=None)
@given(nombre=st.text(max_size=12), datos=st.binary(max_size=300))
def test_ea1_validar_solo_lanza_archivo_rechazado_con_cualquier_entrada(nombre, datos):
    try:
        tipo = archivo.validar(nombre, datos)
    except ArchivoRechazado:
        return
    assert tipo in ("pdf", "imagen", "eml", "txt", "xml")
    archivo.extraer_texto(tipo, datos)                                       # tampoco falla al extraer


# --- aclaraciones.validar_respuesta --------------------------------------------------------------------------
@pytest.mark.parametrize("campo,texto,esperado", [
    ("monto", "1.800.000 COP", "1800000"), ("monto", "mil pesos", None), ("monto", "", None), ("monto", "   ", None),
    ("moneda", "cop", "COP"), ("moneda", "pesos", None), ("moneda", "12", None), ("moneda", "USD dólares", "USD"),
    ("vence", "2026-10-30", "2026-10-30"), ("vence", "pronto", None), ("vence", "", None),
    ("numero", "  IS-2210   extra ", "IS-2210 extra"), ("beneficiario", "Alimentos del Valle", "Alimentos del Valle"),
])
def test_ea5_la_respuesta_del_proveedor_se_limpia_o_se_descarta(campo, texto, esperado):
    r = aclaraciones.validar_respuesta(campo, texto)
    assert (str(r) if r is not None else None) == esperado


def test_ea5_cada_campo_dudoso_tiene_su_pregunta():
    for campo in ("monto", "beneficiario", "moneda", "vence", "numero"):
        assert aclaraciones.pregunta_para(campo).strip()


@settings(max_examples=200, deadline=None)
@given(campo=st.sampled_from(["monto", "beneficiario", "moneda", "vence", "numero"]), texto=st.text(max_size=600))
def test_ea5_ninguna_respuesta_hace_fallar_la_validacion(campo, texto):
    r = aclaraciones.validar_respuesta(campo, texto)
    assert r is None or len(str(r)) <= aclaraciones.LARGO_MAX_MENSAJE
