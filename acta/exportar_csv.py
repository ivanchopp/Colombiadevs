"""CSV generados desde el acta. Spec: specs/acta-y-csv (AC5). Pendiente: los archivos (AT5)."""
from __future__ import annotations

PELIGROSOS = ("=", "+", "-", "@")


def seguro(celda: str) -> str:
    """Antepone un apóstrofo si la celda parece una fórmula, para que una hoja de cálculo
    no la ejecute (AC5.5)."""
    return "'" + celda if celda.startswith(PELIGROSOS) else celda
