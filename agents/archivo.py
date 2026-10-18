"""Recepción del archivo: tipo real, tamaño y texto extraíble (EA1, EA3.1)."""
import email
import io
import re
from email import policy

from .xml_factura import FORMATOS

TAMANO_MAX = 5 * 1024 * 1024
EXTENSIONES = {"pdf": "pdf", "jpg": "imagen", "jpeg": "imagen", "png": "imagen", "eml": "eml", "txt": "txt", "xml": "xml"}


RAICES_XML = {"invoice", "attacheddocument", "autorizacion"} | {r.lower() for f in FORMATOS for r in f["raices"]}
RE_RAIZ = re.compile(r"<(?:[\w.-]+:)?([\w.-]+)[\s>/]")
RE_CODIFICACION = re.compile(rb"""^\s*(?:\xef\xbb\xbf)?<\?xml[^>]*?encoding=["']([\w.-]+)["']""")


class ArchivoRechazado(Exception):
    pass


def _parece_xml(datos: bytes) -> bool:
    return datos.lstrip(b"\xef\xbb\xbf \t\r\n").startswith(b"<")


def detectar_tipo(datos: bytes) -> str | None:
    """Tipo real según los primeros bytes, no según el nombre."""
    if datos.startswith(b"%PDF"):
        return "pdf"
    if datos.startswith(b"\xff\xd8\xff") or datos.startswith(b"\x89PNG\r\n\x1a\n"):
        return "imagen"
    try:
        texto = datos.decode("utf-8")
    except UnicodeDecodeError:
        return "xml" if RE_CODIFICACION.match(datos) else None              # EA11.8: p. ej. ISO-8859-1 (Chile)
    if "\x00" in texto:
        return None
    primeras = texto.lstrip("\ufeff \t\r\n")[:2000].lower()
    raiz = RE_RAIZ.match(primeras)
    if primeras.startswith("<?xml") or (raiz and raiz.group(1) in RAICES_XML):
        return "xml"
    return "eml" if ("\nsubject:" in "\n" + primeras and "\nfrom:" in "\n" + primeras) else "txt"


def validar(nombre: str, datos: bytes) -> str:
    """Devuelve el tipo (pdf, imagen, eml, txt, xml) o lanza ArchivoRechazado."""
    if not datos:
        raise ArchivoRechazado("El archivo está vacío.")
    if len(datos) > TAMANO_MAX:
        raise ArchivoRechazado("El archivo supera 5 MB.")
    ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    if ext not in EXTENSIONES:
        raise ArchivoRechazado("Solo se aceptan PDF, JPG, PNG, EML, TXT o XML.")
    real = detectar_tipo(datos)
    if real is None:
        raise ArchivoRechazado("No reconozco el contenido del archivo.")
    esperado = EXTENSIONES[ext]
    if esperado == "xml" and real == "txt" and _parece_xml(datos):
        real = "xml"                                   # EA11.7: XML sin declaración de un formato no reconocido
    if real != esperado and not (esperado == "txt" and real == "eml") and not (esperado == "eml" and real == "txt"):
        raise ArchivoRechazado("El contenido del archivo no coincide con su extensión.")
    return real


def extraer_texto(tipo: str, datos: bytes) -> str | None:
    """Texto de la factura, o None si no hay (imágenes)."""
    if tipo == "imagen":
        return None
    if tipo == "pdf":
        try:
            from pypdf import PdfReader
            lector = PdfReader(io.BytesIO(datos))
            return "\n".join((p.extract_text() or "") for p in lector.pages[:10]) or None
        except Exception:
            return None
    codificacion = RE_CODIFICACION.match(datos) if tipo == "xml" else None
    try:
        texto = datos.decode(codificacion.group(1).decode() if codificacion else "utf-8", errors="replace")
    except LookupError:
        texto = datos.decode("utf-8", errors="replace")
    if tipo == "eml":
        try:
            msg = email.message_from_string(texto, policy=policy.default)
            cuerpo = msg.get_body(preferencelist=("plain",))
            partes = [f"De: {msg.get('From', '')}", f"Asunto: {msg.get('Subject', '')}",
                      cuerpo.get_content() if cuerpo else ""]
            return "\n".join(partes)
        except Exception:
            return texto
    return texto
