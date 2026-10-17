"""Orquestador del motor de reglas: función pura, sin IA y sin red.

Spec: specs/motor-de-reglas (R1, R10). Reglas de oro:
  - PAGAR solo si hay revisiones y todas son OK (R1.2). Sin revisiones configuradas, nunca se paga.
  - Si una revisión falla o lanza una excepción, el resultado es ESCALAR (R1.3).
  - Se evalúan todas las revisiones, aunque una falle (R1.5).
"""
from __future__ import annotations

from collections.abc import Callable, Sequence

from engine.modelos import Contexto, Decision, Ficha, Nivel, Resultado, Reglas, Revision
from engine.niveles import nivel_maximo

Revisar = Callable[[Ficha, Contexto, Reglas], Revision]

# Las revisiones reales se registran aquí a medida que se implementan (tareas T4 a T7).
REVISIONES: tuple[Revisar, ...] = ()


def resolver(revisiones: Sequence[Revision]) -> Decision:
    """La decisión más severa gana: FRENAR sobre ESCALAR, y ESCALAR sobre PAGAR (R1.4)."""
    if not revisiones:
        return "ESCALAR"                       # sin revisiones no hay base para pagar
    if any(r.efecto == "FRENAR" and r.resultado != "OK" for r in revisiones):
        return "FRENAR"
    if any(r.resultado != "OK" for r in revisiones):
        return "ESCALAR"
    return "PAGAR"


def _fallo_de_evaluacion(revision: Revisar, error: Exception) -> Revision:
    """Una revisión que no se pudo evaluar cuenta como FALLA que escala (R1.3)."""
    return Revision(
        regla=getattr(revision, "__name__", "revision"),
        resultado="FALLA",
        efecto="ESCALAR",
        nivel="PERSONA",
        observado="no se pudo evaluar",
        umbral="—",
        mensaje=f"No se pudo evaluar esta revisión ({type(error).__name__}).",
    )


def evaluar(
    ficha: Ficha,
    contexto: Contexto,
    reglas: Reglas,
    revisiones: Sequence[Revisar] | None = None,
) -> Resultado:
    """Devuelve la decisión, el nivel, las revisiones y el motivo de una ficha."""
    a_correr = REVISIONES if revisiones is None else tuple(revisiones)
    resultados: list[Revision] = []
    for revision in a_correr:
        try:
            resultados.append(revision(ficha, contexto, reglas))
        except Exception as error:             # noqa: BLE001 — fallo seguro (R1.3)
            resultados.append(_fallo_de_evaluacion(revision, error))

    decision = resolver(resultados)
    niveles: list[Nivel] = [r.nivel for r in resultados]   # una revisión OK que exige nivel también cuenta
    nivel = nivel_maximo(niveles)
    if decision == "PAGAR" and nivel != "NINGUNO":   # R1.2
        decision = "ESCALAR"
    if decision == "ESCALAR" and nivel == "NINGUNO":
        nivel = "PERSONA"                            # toda escalada tiene un nivel que la resuelve

    motivo = (
        "Sin revisiones configuradas: se escala para que decida una persona."
        if not resultados
        else "; ".join(r.mensaje for r in resultados if r.resultado != "OK") or "Cumple todas las reglas."
    )
    return Resultado(
        decision=decision,
        nivel=nivel,
        revisiones=resultados,
        motivo=motivo,
        version_reglas=reglas.version,
    )
