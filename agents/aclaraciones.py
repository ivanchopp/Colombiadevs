"""Preguntas de plantilla y validación de respuestas (EA5). Sin IA."""
from datetime import date

from .segunda_lectura import parsear_fecha, parsear_monto

TURNOS_MAX = 2
LARGO_MAX_MENSAJE = 500

PREGUNTAS = {
    "beneficiario": "¿Puedes confirmarme el nombre completo de quien cobra?",
    "numero": "¿Cuál es el número de la factura?",
    "monto": "¿Cuál es el monto total de la factura, sin la moneda?",
    "moneda": "¿En qué moneda es la factura? (por ejemplo COP o USD)",
    "vence": "¿Cuál es la fecha de vencimiento? (por ejemplo 2026-10-30)",
}


def pregunta_para(campo: str) -> str:
    return PREGUNTAS[campo]


def validar_respuesta(campo: str, texto: str):
    """Valor limpio, o None si la respuesta no sirve para ese campo."""
    t = (texto or "").strip()[:LARGO_MAX_MENSAJE]
    if not t:
        return None
    if campo == "monto":
        return parsear_monto(t.split()[0])
    if campo == "moneda":
        c = t.split()[0].upper()
        return c if len(c) == 3 and c.isalpha() else None
    if campo == "vence":
        f = parsear_fecha(t.split()[0])
        return f.isoformat() if isinstance(f, date) else None
    return " ".join(t.split())[:80]
