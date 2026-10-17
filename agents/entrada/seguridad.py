"""Depurar el texto, delimitarlo como datos y detectar órdenes escondidas.

Spec: specs/extraccion-y-agente-de-entrada (EX5.1, EX5.3, EX5.4). Tarea ET7.
Primera versión de los patrones: el equipo la amplía con las pruebas de EX9.4.
"""
from __future__ import annotations

import re
import unicodedata

CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
ETIQUETAS_HTML = re.compile(r"<[^>]{0,200}>")

# Frases que intentan dar órdenes, en español y en inglés.
PATRONES_DE_ORDENES = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"ignor[ae]\w*\s+(las\s+)?(instrucciones|reglas)",
        r"ignore\s+(all\s+|the\s+|previous\s+)?(instructions|rules)",
        r"aprobad[ao]\s+por",
        r"approved\s+by",
        r"\bpag(a|ar|uen|ue)\s+(ya|hoy|ahora|ahora\s+mismo|esta\s+factura)\b",
        r"pay\s+(this\s+)?(now|immediately)",
        r"no\s+(escales|escalen|revises|revisen)",
        r"do\s+not\s+(escalate|review)",
        r"ya\s+est[aá]\s+aprobad[ao]",
    )
)


def depurar(texto: str, max_caracteres: int = 20_000) -> str:
    """Quita caracteres de control y etiquetas HTML, normaliza y corta el largo (EX5.3)."""
    texto = unicodedata.normalize("NFKC", texto)
    texto = CONTROL.sub(" ", texto)
    texto = ETIQUETAS_HTML.sub(" ", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    return texto[:max_caracteres]


def delimitar(texto: str) -> str:
    """Envuelve el texto como datos, para que el modelo no lo trate como instrucciones (EX5.1)."""
    # Una etiqueta de cierre dentro del texto no puede salirse del bloque.
    seguro = texto.replace("</factura>", "<\\/factura>")
    return f"<factura>\n{seguro}\n</factura>"


def detectar_ordenes(texto: str) -> bool:
    """True si el texto contiene frases que intentan dar órdenes (EX5.4). Solo informa."""
    return any(p.search(texto) for p in PATRONES_DE_ORDENES)
