"""Tipos de evento del acta. Spec: specs/acta-y-csv (AC1.3, AC3). Payloads pendientes (AT3)."""
from __future__ import annotations

TIPOS_DE_EVENTO: tuple[str, ...] = (
    "DECISION",
    "APROBACION",
    "RECHAZO",
    "CAMBIO_REGLA",
    "INTENTO_RECHAZADO",
    "REVISION_CONCILIACION",
    "CIERRE_PERIODO",
)
