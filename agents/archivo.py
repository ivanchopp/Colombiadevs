"""Recepción del archivo: tipo real, tamaño y texto extraíble (EA1, EA3.1)."""
import email
import io
from email import policy

TAMANO_MAX = 5 * 1024 * 1024
EXTENSIONES = {"pdf": "pdf", "jpg": "imagen", "jpeg": "imagen", "png": "imagen", "eml": "eml", "txt": "txt"}


class ArchivoRechazado(Exception):
    pass


def detectar_tipo(datos: bytes) -> str | None:
    """Tipo real según los primeros bytes, no según el nombre."""
    if datos.startswith(b"%PDF"):
        return "pdf"
    if datos.startswith(b"\xff\xd8\xff") or datos.startswith(b"\x89PNG\r\n\x1a\n"):
        return "imagen"
    try:
        texto = datos.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if "\x00" in texto:
        return None
    primeras = texto.lstrip()[:2000].lower()
    return "eml" if ("\nsubject:" in "\n" + primeras and "\nfrom:" in "\n" + primeras) else "txt"


def validar(nombre: str, datos: bytes) -> str:
    """Devuelve el tipo (pdf, imagen, eml, txt) o lanza ArchivoRechazado."""
    if not datos:
        raise ArchivoRechazado("El archivo está vacío.")
    if len(datos) > TAMANO_MAX:
        raise ArchivoRechazado("El archivo supera 5 MB.")
    ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    if ext not in EXTENSIONES:
        raise ArchivoRechazado("Solo se aceptan PDF, JPG, PNG, EML o TXT.")
    real = detectar_tipo(datos)
    if real is None:
        raise ArchivoRechazado("No reconozco el contenido del archivo.")
    esperado = EXTENSIONES[ext]
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
