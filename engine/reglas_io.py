"""Carga de reglas desde YAML con esquema cerrado.

Spec: specs/motor-de-reglas (R9.1, R9.3). Pendiente: vigencias, conflictos, afloja/restringe y
techos duros (R9.2, R9.4, R9.5, tarea T12, capa 3).
"""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from engine.modelos import Reglas

RUTA_REGLAS = Path(__file__).resolve().parents[1] / "data" / "reglas.yaml"


def cargar_reglas(ruta: Path | str = RUTA_REGLAS) -> Reglas:
    """Lee y valida un YAML de reglas. Lanza un error si no cumple el esquema (R9.1)."""
    datos = yaml.safe_load(Path(ruta).read_text(encoding="utf-8"))
    return Reglas.model_validate(datos)


def cargar_reglas_o_anterior(ruta: Path | str, anterior: Reglas) -> tuple[Reglas, str | None]:
    """Si el archivo es inválido, conserva la última versión válida y devuelve el error (R9.1)."""
    try:
        return cargar_reglas(ruta), None
    except (ValidationError, yaml.YAMLError, OSError, TypeError) as error:
        return anterior, f"Reglas no cargadas: {error}"


def cambio_afloja(antes: Reglas, despues: Reglas) -> bool:
    """R9.4. Pendiente (T12)."""
    raise NotImplementedError("Tarea T12 (capa 3): detectar si un cambio afloja una regla")
