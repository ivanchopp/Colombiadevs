"""Preguntas al proveedor con plantillas fijas. Spec: extracción (EX4). Tarea ET6 (capa 3).

Pendiente: calcular los campos a aclarar, aplicar respuestas y llevar los turnos.
"""
from __future__ import annotations

MAX_TURNOS = 2  # valor de demostración, ver la spec (parámetro `max_turnos`)

# Una plantilla por campo (design.md). `{numero}` es el número de la factura.
PLANTILLAS: dict[str, str] = {
    "monto": "¿Cuál es el valor total a pagar de la factura {numero}?",
    "moneda": "¿En qué moneda está la factura?",
    "vence": "¿Cuál es la fecha de vencimiento?",
    "beneficiario": "¿A nombre de quién debe estar el pago?",
    "cuenta": "¿Puedes confirmar el banco y los últimos dígitos de la cuenta donde recibes el pago?",
}


def armar_pregunta(campos: list[str], numero: str | None) -> str:
    """Agrupa las dudas en una sola pregunta, solo con las plantillas (EX4.2, EX4.3)."""
    desconocidos = [c for c in campos if c not in PLANTILLAS]
    if desconocidos:
        raise ValueError(f"campos sin plantilla: {desconocidos}")
    return " ".join(PLANTILLAS[c].format(numero=numero or "") for c in campos).strip()
