"""Mide autonomía, seguridad y explicabilidad con los 20 casos (R11.3, R11.4). Control de las 18:00."""
import sys
import time
from datetime import date
from pathlib import Path

import yaml

from engine.evaluar import evaluar
from engine.compras import normalizar_oc
from engine.modelos import Movimiento, Obligacion
from engine.reglas_io import DATA, cargar_contexto_base, cargar_reglas


def correr(ruta=DATA / "casos.yaml"):
    datos = yaml.safe_load(Path(ruta).read_text(encoding="utf-8"))
    hoy = date.fromisoformat(str(datos["hoy"]))
    reglas, _ = cargar_reglas(hoy)
    base = cargar_contexto_base(hoy)
    filas = []
    for caso in datos["casos"]:
        ctx = base.model_copy(update={"historial": base.historial + [
            Movimiento.model_validate(m) for m in caso.get("historial_extra", [])],
            "calendario": base.calendario + [Obligacion.model_validate(o) for o in caso.get("calendario_extra", [])],
            "oc_facturadas": {normalizar_oc(k): v for k, v in caso.get("oc_facturadas", {}).items()}})
        t0 = time.perf_counter()
        r = evaluar(caso["ficha"], ctx, reglas)
        ms = (time.perf_counter() - t0) * 1000
        esp = caso["esperado"]
        filas.append(dict(caso=caso, resultado=r, ms=ms,
                          bien=(r.decision, r.nivel) == (esp["decision"], esp["nivel"]),
                          indebido=r.decision == "PAGAR" and esp["decision"] != "PAGAR"))
    return filas


def main():
    filas = correr()
    for f in filas:
        r, c = f["resultado"], f["caso"]
        marca = "OK " if f["bien"] else "MAL"
        print(f"{marca} {c['id']} {c['nombre'][:38]:<38} esperado {c['esperado']['decision']}/{c['esperado']['nivel']:<8}"
              f" obtuvo {r.decision}/{r.nivel:<8} {f['ms']:.1f} ms")
        if not f["bien"]:
            print("      motivo:", r.motivo)
    n = len(filas)
    ok = sum(f["bien"] for f in filas)
    indebidos = sum(f["indebido"] for f in filas)
    explicados = sum(bool(f["resultado"].motivo and f["resultado"].revisiones) for f in filas)
    lento = max(f["ms"] for f in filas)
    print(f"\nAutonomía:      {ok}/{n} casos con la decisión y el nivel esperados")
    print(f"Seguridad:      {indebidos} pagos indebidos (debe ser 0)")
    print(f"Explicabilidad: {explicados}/{n} decisiones con motivo y revisiones")
    print(f"Velocidad:      la más lenta tardó {lento:.1f} ms (límite 200 ms)")
    sys.exit(0 if indebidos == 0 and ok == n and explicados == n and lento < 200 else 1)


if __name__ == "__main__":
    main()
