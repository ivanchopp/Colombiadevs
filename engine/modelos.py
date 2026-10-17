"""Modelos cerrados del motor de reglas.

Spec: specs/motor-de-reglas (tarea T1; criterios R1.1, R2.1, R10.1).
Todos los modelos rechazan campos que no conocen (esquema cerrado). El dinero va en `Decimal`.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Decision = Literal["PAGAR", "FRENAR", "ESCALAR"]
Nivel = Literal["NINGUNO", "PERSONA", "SENIOR"]
ResultadoRevision = Literal["OK", "FALLA", "AVISO"]
Efecto = Literal["FRENAR", "ESCALAR", "NINGUNO"]


class Cerrado(BaseModel):
    """Base: un campo desconocido es un error (R2.1)."""

    model_config = ConfigDict(extra="forbid")


class Aclaracion(Cerrado):
    """Un turno de aclaración con el proveedor (spec extracción, EX4.10)."""

    turno: int = Field(ge=1)
    pregunta: str
    respuesta: str
    campos: list[str]


class Ficha(Cerrado):
    """Datos ordenados de una factura. La entrega el agente de entrada.

    Los campos obligatorios pueden venir en `None`: el motor los escala (R1.3, EX6.3).
    La ficha NO lleva el texto libre de la factura (R2.4, EX5.5).
    """

    factura_id: str
    beneficiario: str | None
    numero: str | None
    monto: Decimal | None = Field(default=None, gt=0)
    moneda: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")
    vence: date | None
    cuenta_original: str | None = None
    cuenta_aclarada: str | None = None
    valores_aclarados: dict[str, Any] = Field(default_factory=dict)
    origen_campos: dict[str, Literal["factura", "aclarado"]] = Field(default_factory=dict)
    lectura_ia: Literal["ok", "dudosa"]
    segunda_lectura: Literal["coincide", "no_coincide", "no_disponible"]
    campos_diferentes: list[str] = Field(default_factory=list)
    alerta_inyeccion: bool = False
    aclaraciones: list[Aclaracion] = Field(default_factory=list)
    preparador: str


class Revision(Cerrado):
    """Resultado de una regla sobre una ficha (R10.1)."""

    regla: str                      # por ejemplo "R3.1"
    resultado: ResultadoRevision
    efecto: Efecto                  # qué decisión empuja si no es OK
    nivel: Nivel                    # nivel de aprobación que exige
    observado: str
    umbral: str
    mensaje: str


class CanalSugerido(Cerrado):
    """Un canal evaluado para pagar (R7). Costos y tiempos son «supuesto» (R7.4)."""

    canal: str
    etiqueta: Literal["Sugerido", "Alternativa", "Revisar", "No sugerido"]
    encaja: str
    costo: str | None = None        # None se muestra como «sin dato»
    tiempo: str | None = None
    supuesto: bool = True


class Resultado(Cerrado):
    """Lo que devuelve `evaluar` (R10.1)."""

    decision: Decision
    nivel: Nivel
    revisiones: list[Revision]
    motivo: str
    version_reglas: str
    tasa_usada: Decimal | None = None
    canal: CanalSugerido | None = None
    canales_evaluados: list[CanalSugerido] = Field(default_factory=list)


class Reglas(Cerrado):
    """Parámetros vigentes. Sin valores por defecto en el código: salen de data/reglas.yaml."""

    version: str
    vigente_desde: date
    vigente_hasta: date | None
    supuesto: bool
    moneda_base: str = Field(pattern=r"^[A-Z]{3}$")
    autopago_max: Decimal = Field(gt=0)
    persona_max: Decimal = Field(gt=0)
    limite_periodo_beneficiario: Decimal = Field(gt=0)
    presupuesto_periodo: Decimal = Field(gt=0)
    tolerancia_ok: Decimal = Field(ge=0)
    tolerancia_frenar: Decimal = Field(ge=0)
    ventana_dias: int = Field(ge=0)
    dias_gracia: int = Field(ge=0)


class Contexto(Cerrado):
    """Registros de la empresa que el motor consulta (beneficiarios, historial, acuerdos,
    presupuesto, calendario, tasas y canales).

    La forma exacta de cada parte se define en la tarea T2 junto con los datos semilla.
    Hasta entonces se guardan como diccionarios sin interpretar.
    """

    beneficiarios: dict[str, Any] = Field(default_factory=dict)
    historial: list[dict[str, Any]] = Field(default_factory=list)
    acuerdos: dict[str, Any] = Field(default_factory=dict)
    calendario: list[dict[str, Any]] = Field(default_factory=list)
    tasas: dict[str, Any] = Field(default_factory=dict)
    canales: list[dict[str, Any]] = Field(default_factory=list)
    gasto_periodo: Decimal = Decimal("0")
