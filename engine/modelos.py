"""Modelos cerrados (Pydantic). Dinero siempre con Decimal."""
from datetime import date
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Decision = Literal["PAGAR", "FRENAR", "ESCALAR"]
Nivel = Literal["NINGUNO", "PERSONA", "SENIOR"]
RANGO = {"NINGUNO": 0, "PERSONA": 1, "SENIOR": 2}


class Cerrado(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Ficha(Cerrado):
    factura_id: str = Field(min_length=1)
    beneficiario: str = Field(min_length=1)
    numero: str = Field(min_length=1)
    monto: Decimal = Field(gt=0)
    moneda: str = Field(pattern=r"^[A-Z]{3}$")
    vence: date
    recibida: date
    cuenta_original: str | None = None
    cuenta_aclarada: str | None = None
    valores_aclarados: dict[str, Any] = {}
    origen_campos: dict[Literal["beneficiario", "numero", "monto", "moneda", "vence"],
                        Literal["factura", "aclarado"]] = {}
    lectura_ia: Literal["ok", "dudosa"]
    segunda_lectura: Literal["coincide", "no_coincide", "no_disponible"]
    orden_en_texto: bool = False
    preparador: str = Field(min_length=1)

    @field_validator("monto", mode="before")
    @classmethod
    def _sin_float(cls, v):
        if isinstance(v, float):
            raise ValueError("el monto no puede ser float")
        return v


class Registro(Cerrado):
    pais: str
    cuenta: str
    acuerdo_monto: Decimal | None = None
    acuerdo_moneda: str | None = None


class Obligacion(Cerrado):
    id: str
    beneficiario: str
    fecha: date
    monto_base: Decimal
    factura_id: str | None = None          # la factura que ya la cubrió


class Movimiento(Cerrado):
    factura_id: str
    beneficiario: str
    numero: str
    monto: Decimal
    moneda: str
    vence: date
    monto_base: Decimal
    estado: Literal["PAGADA", "PENDIENTE", "FRENADA", "RECHAZADA"]
    periodo: str                            # "AAAA-MM"


class CanalDef(Cerrado):
    nombre: str
    paises: list[str]                       # ["*"] = cualquiera
    monedas: list[str]
    costo: Literal["bajo", "medio", "alto"] | None = None
    tiempo_horas: Decimal | None = None
    requiere_verificacion: bool = False
    supuesto: bool = True


class Contexto(Cerrado):
    hoy: date
    registros: dict[str, Registro]
    tasas: dict[str, Decimal]
    historial: list[Movimiento] = []
    calendario: list[Obligacion] = []
    canales: list[CanalDef] = []

    @property
    def periodo(self) -> str:
        return f"{self.hoy.year:04d}-{self.hoy.month:02d}"


class Reglas(Cerrado):
    version: str
    vigente_desde: date | None = None
    moneda_base: str = "COP"
    autopago_max: Decimal
    persona_max: Decimal
    techo_duro_pago: Decimal
    limite_periodo_beneficiario: Decimal
    presupuesto_periodo: Decimal
    tolerancia_ok: Decimal
    tolerancia_frenar: Decimal
    ventana_dias: int
    dias_gracia: int


class Revision(Cerrado):
    regla: str
    resultado: Literal["OK", "FALLA", "AVISO"]
    efecto: Literal["FRENAR", "ESCALAR", "NINGUNO"] = "NINGUNO"
    nivel: Nivel = "NINGUNO"
    observado: str = ""
    umbral: str = ""
    mensaje: str


class CanalEvaluado(Cerrado):
    nombre: str
    etiqueta: Literal["Sugerido", "Alternativa", "Revisar", "No sugerido"]
    razon: str
    costo: str                              # "bajo", "medio", "alto" o "sin dato"
    tiempo_horas: Decimal | None = None
    supuesto: bool = True


class CanalSugerido(Cerrado):
    sugerido: str | None
    evaluados: list[CanalEvaluado]
    aviso: str | None = None


class Resultado(Cerrado):
    decision: Decision
    nivel: Nivel
    revisiones: list[Revision]
    motivo: str
    version_reglas: str
    tasa_usada: Decimal | None = None
    monto_base: Decimal | None = None
    canal: CanalSugerido | None = None
    obligacion_id: str | None = None


def nivel_max(*niveles: str) -> str:
    return max(niveles, key=RANGO.__getitem__, default="NINGUNO")
