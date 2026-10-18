"""Qué decisiones de la sala cambiarían con otras reglas (R9.6). No escribe nada."""
from .evaluar import evaluar


def simular(filas, ctx, antes, despues) -> list[dict]:
    """Vuelve a evaluar la ficha guardada de cada decisión con las dos versiones de reglas, sobre el
    mismo contexto, y devuelve solo las que cambian."""
    cambian = []
    for f in filas:
        if f.tipo != "DECISION" or "ficha" not in f.payload:
            continue
        a, d = evaluar(f.payload["ficha"], ctx, antes), evaluar(f.payload["ficha"], ctx, despues)
        if (a.decision, a.nivel) != (d.decision, d.nivel):
            cambian.append({"factura_id": f.factura_id, "beneficiario": f.payload["beneficiario"],
                            "antes": f"{a.decision} / {a.nivel}", "despues": f"{d.decision} / {d.nivel}",
                            "motivo": d.motivo})
    return cambian
