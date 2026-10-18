"""Carga de reglas, techos y datos base desde data/ (R9.1, R9.3)."""
import csv
import os
from datetime import date
from decimal import Decimal
from pathlib import Path

import yaml
from pydantic import ValidationError

from .compras import cargar_compras
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


PAIS_ISO = {"Colombia": "CO", "México": "MX", "Perú": "PE", "Ecuador": "EC"}


def registros_de_proveedores(proveedores: dict, acuerdos: dict, historial: list) -> dict[str, Registro]:
    """Lista permitida (R4.1) y cuenta (R4.2) desde proveedores.yaml, con el acuerdo de registros.yaml (OC1.6).
    Un acuerdo o un movimiento de un proveedor que no está en el registro es un error de datos: falla."""
    registros = {p["nombre"]: Registro(pais=PAIS_ISO.get(p["pais"], p["pais"]), cuenta=p["cuenta"])
                 for p in proveedores["proveedores"]}
    sobran = sorted({*acuerdos} - {*registros} | {m["beneficiario"] for m in historial} - {*registros})
    if sobran:
        raise ErrorDeReglas(f"registros.yaml nombra proveedores que no están en proveedores.yaml: {sobran}")
    for nombre, a in acuerdos.items():
        registros[nombre] = registros[nombre].model_copy(update={
            "acuerdo_monto": Decimal(str(a["monto"])), "acuerdo_moneda": a["moneda"]})
    return registros


def cargar_contexto_base(hoy: date, carpeta=None) -> Contexto:
    reg = _yaml("registros.yaml", carpeta)
    tasas = _yaml("tasas.yaml", carpeta)["tasas"]
    canales = _yaml("canales.yaml", carpeta)["canales"]
    ruta = Path(carpeta or DATA) / "calendario.csv"
    with ruta.open(encoding="utf-8", newline="") as f:
        calendario = [Obligacion(id=r["id"], beneficiario=r["beneficiario"],
                                 fecha=date.fromisoformat(r["fecha"]), monto_base=Decimal(r["monto_base"]))
                      for r in csv.DictReader(f)]
    proveedores, ordenes = cargar_compras(carpeta)
    return Contexto(
        hoy=hoy,
        registros=registros_de_proveedores(_yaml("proveedores.yaml", carpeta), reg.get("acuerdos", {}),
                                           reg.get("historial", [])),
        proveedores=proveedores,
        ordenes=ordenes,
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


# --- Cambios de reglas por sala (PP8, R9.4, R9.5) ---------------------------------------------
EDITABLES = ("autopago_max", "persona_max", "limite_periodo_beneficiario", "presupuesto_periodo",
             "tolerancia_ok", "tolerancia_frenar", "ventana_dias")
UMBRALES_DE_MONTO = ("autopago_max", "persona_max", "limite_periodo_beneficiario")


def reglas_de_sala(base: Reglas, filas) -> Reglas:
    """Reglas vigentes más el último CAMBIO_REGLA de la sala. Versión: «v12.s2» (PP8.7)."""
    cambios = [f for f in filas if f.tipo == "CAMBIO_REGLA"]
    if not cambios:
        return base
    despues = cambios[-1].payload["despues"]
    return Reglas.model_validate({**base.model_dump(), **{k: despues[k] for k in EDITABLES},
                                  "version": f"{base.version}.s{len(cambios)}"})


def cambios_que_aflojan(antes: Reglas, despues: Reglas) -> list[str]:
    """Todo parámetro editable que sube afloja: deja pasar más sin una persona (R9.4)."""
    return [k for k in EDITABLES if getattr(despues, k) > getattr(antes, k)]


def validar_cambio(antes: Reglas, valores: dict) -> Reglas:
    """Devuelve las reglas nuevas o lanza ErrorDeReglas con una explicación (PP8.5, R9.5)."""
    try:
        nuevas = Reglas.model_validate({**antes.model_dump(),
                                        **{k: valores[k] for k in EDITABLES if k in valores}})
    except ValidationError as e:
        raise ErrorDeReglas(f"Valores inválidos: {e.errors()[0]['msg']}") from e
    if any(getattr(nuevas, k) <= 0 for k in EDITABLES if k != "ventana_dias") or nuevas.ventana_dias < 0:
        raise ErrorDeReglas("Los montos y las tolerancias deben ser mayores que cero.")
    if nuevas.autopago_max > nuevas.persona_max:
        raise ErrorDeReglas("El pago automático no puede superar lo que aprueba la persona de finanzas.")
    if not nuevas.tolerancia_ok <= nuevas.tolerancia_frenar <= 1:
        raise ErrorDeReglas("La tolerancia normal debe ser menor o igual a la de frenar, y esta como máximo 100 %.")
    if nuevas.ventana_dias > 31:
        raise ErrorDeReglas("La ventana del calendario no puede pasar de 31 días.")
    sobre_techo = [k for k in UMBRALES_DE_MONTO if getattr(nuevas, k) > antes.techo_duro_pago]
    if sobre_techo:
        raise ErrorDeReglas(f"Supera el techo duro ({antes.techo_duro_pago}): {', '.join(sobre_techo)}. "
                            "El techo duro no se cambia desde la aplicación.")
    return nuevas
