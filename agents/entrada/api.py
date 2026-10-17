"""Interfaz pública del agente de entrada: lo que usan los paneles y el motor de reglas.

Spec: specs/extraccion-y-agente-de-entrada, design.md («Interfaz pública»).
`procesar` nunca llama al motor de reglas ni escribe en el acta: devuelve la ficha.
Esqueleto: aún sin implementar.
"""
from __future__ import annotations

from typing import Literal

from engine.modelos import Ficha


def procesar(archivo, sala_id: str, preparador: str) -> Ficha:
    """Recepción, lectura, extracción, segunda lectura y ficha (EX1 a EX3, EX6)."""
    raise NotImplementedError("Tareas ET1 a ET5: procesar")


def pregunta_pendiente(sala_id: str, factura_id: str) -> str | None:
    """La pregunta del agente, si espera una respuesta del proveedor (EX4). Capa 3 (ET6)."""
    raise NotImplementedError("Tarea ET6 (capa 3): pregunta_pendiente")


def responder(sala_id: str, factura_id: str, texto: str) -> Ficha:
    """Aplica la respuesta del proveedor a la ficha (EX4.7 a EX4.9). Capa 3 (ET6)."""
    raise NotImplementedError("Tarea ET6 (capa 3): responder")


def etapa_de_lectura(sala_id: str, factura_id: str) -> Literal["recibida", "datos_confirmados"]:
    """Alimenta el estado público del Panel 1 (PD3.5)."""
    raise NotImplementedError("Tarea ET5: etapa_de_lectura")
