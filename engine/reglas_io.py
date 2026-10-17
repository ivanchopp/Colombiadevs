"""Carga de reglas, techos y datos base desde data/ (R9.1, R9.3)."""
import csv
import os
from datetime import date
from decimal import Decimal
from pathlib import Path

import yaml
from pydantic import ValidationError

from .modelos import CanalDef, Contexto, Movimiento, Obligacion, Registro, Reglas

from zoneinfo import ZoneInfo
from datetime import datetime

DATA = Path(__file__).resolve().parent.parent / "data"


class ErrorDeReglas(Exception):
    pass


def _yaml(nombre, carpeta=None):
    return yaml.safe_load((Path(carpeta or DATA) / nombre).read_text(encoding="utf-8"))


def cargar_reglas(hoy: date, carpeta=None, anterior: Reglas | None = None):
    """Devuelve (reglas, error). Si el archivo es inválido conserva la versión anterior (R9.1)."""
    try:
        conjuntos = _yaml("reglas.yaml", carpeta)["conjuntos"]
        vigentes = [c for c in conjuntos if (c.get("vigente_hasta") is None or c["vigente_hasta"] >= hoy)
                    and c["vigente_desde"] <= hoy]
        elegido = max(vigentes, key=lambda c: c["vigente_desde"])
        elegido = {k: v for k, v in elegido.items() if k != "vigente_hasta"}
        reglas = Reglas.model_validate(elegido)
        techo = Decimal(str(_yaml("techos.yaml", carpeta)["techo_duro_pago"]))
        if reglas.techo_duro_pago > techo:                               # R9.5: el techo duro manda
            reglas = reglas.model_copy(update={"techo_duro_pago": techo})
        return reglas, None
    except (ValidationError, KeyError, ValueError, TypeError, OSError, yaml.YAMLError) as e:
        if anterior is None:
            raise ErrorDeReglas(f"reglas.yaml inválido y sin versión anterior: {e}") from e
        return anterior, f"reglas.yaml inválido; se conserva {anterior.version}: {e}"


def cargar_contexto_base(hoy: date, carpeta=None) -> Contexto:
    reg = _yaml("registros.yaml", carpeta)
    tasas = _yaml("tasas.yaml", carpeta)["tasas"]
    canales = _yaml("canales.yaml", carpeta)["canales"]
    ruta = Path(carpeta or DATA) / "calendario.csv"
    with ruta.open(encoding="utf-8", newline="") as f:
        calendario = [Obligacion(id=r["id"], beneficiario=r["beneficiario"],
                                 fecha=date.fromisoformat(r["fecha"]), monto_base=Decimal(r["monto_base"]))
                      for r in csv.DictReader(f)]
    return Contexto(
        hoy=hoy,
        registros={k: Registro.model_validate(v) for k, v in reg["beneficiarios"].items()},
        tasas={k: Decimal(str(v)) for k, v in tasas.items()},
        historial=[Movimiento.model_validate(m) for m in reg.get("historial", [])],
        calendario=calendario,
        canales=[CanalDef.model_validate(c) for c in canales])


def hoy_bogota() -> date:
    """«Hoy» en Bogotá. FECHA_DEMO (AAAA-MM-DD) lo fija para que la demo no dependa del día (PD1.5)."""
    fija = os.environ.get("FECHA_DEMO")
    if fija:
        try:
            return date.fromisoformat(fija)
        except ValueError:
            pass
    return datetime.now(ZoneInfo("America/Bogota")).date()
