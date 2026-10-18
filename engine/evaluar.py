"""Orquestador: corre todas las revisiones y resuelve la decisión. Función pura (R1)."""
from pydantic import ValidationError

from .canales import sugerir_canal
from .modelos import Ficha, Resultado, Revision, nivel_max
from .niveles import nivel_de_revisiones
from .revisiones import NoEvaluable, beneficiario, calendario, entrada, frenar, montos, orden_compra
from .revisiones.comun import a_base

# (regla de referencia, función): todas corren, en este orden (R1.5).
REVISIONES = [
    ("R2", entrada.revisar),
    ("R3.1", frenar.duplicado),
    ("R4", beneficiario.revisar),
    ("OC4", orden_compra.revisar),
    ("R6", calendario.revisar),
    ("R3.2", frenar.acuerdo),
    ("R3.6", frenar.presupuesto_y_techo),
    ("R5", montos.revisar),
]


def _fallo(regla, error) -> Revision:
    """Una revisión que no se pudo evaluar nunca deja pasar un pago (R1.3)."""
    nivel = error.nivel if isinstance(error, NoEvaluable) else "SENIOR"
    mensaje = str(error) if isinstance(error, NoEvaluable) else f"No se pudo evaluar {regla}."
    return Revision(regla=regla, resultado="FALLA", efecto="ESCALAR", nivel=nivel,
                    observado="no evaluable", umbral="evaluable", mensaje=mensaje)


def _motivo(decision, nivel, revisiones, obligacion_id) -> str:
    if decision == "PAGAR":
        return "Cumple todas las reglas" + (" y estaba en el calendario." if obligacion_id else ".")
    malas = [r for r in revisiones if r.resultado != "OK"]
    if decision == "FRENAR":
        malas = [r for r in malas if r.efecto == "FRENAR"]
    malas.sort(key=lambda r: (r.efecto != "FRENAR", -["NINGUNO", "PERSONA", "SENIOR"].index(r.nivel)))
    causas = []
    for r in malas:
        m = r.mensaje.rstrip(".")
        if m not in causas:
            causas.append(m)
    texto = "; ".join(causas[:2]) + "."
    if decision == "ESCALAR":
        texto += " Lo aprueba " + ("el senior de finanzas." if nivel == "SENIOR" else "la persona de finanzas.")
    return texto


def _ficha_invalida(reglas, error) -> Resultado:
    campos = ", ".join(sorted({str(e["loc"][0]) for e in error.errors() if e["loc"]})) or "ficha"
    rev = Revision(regla="R2.1", resultado="FALLA", efecto="ESCALAR", nivel="SENIOR",
                   observado=campos, umbral="esquema cerrado", mensaje="Ficha inválida.")
    return Resultado(decision="ESCALAR", nivel="SENIOR", revisiones=[rev],
                     motivo=(f"Ficha inválida: faltan o no se pudieron leer datos obligatorios ({campos}). Una persona debe "
                             "revisarla; no se puede aprobar un pago sin esos datos."),
                     version_reglas=reglas.version)


def evaluar(ficha, ctx, reglas) -> Resultado:
    try:
        f = ficha if isinstance(ficha, Ficha) else Ficha.model_validate(ficha)
    except ValidationError as e:                                         # R2.1
        return _ficha_invalida(reglas, e)

    revisiones: list[Revision] = []
    for regla, revision in REVISIONES:
        try:
            revisiones.extend(revision(f, ctx, reglas))
        except Exception as e:                                           # R1.3
            revisiones.append(_fallo(regla, e))

    if any(r.efecto == "FRENAR" for r in revisiones):                    # R1.4
        decision = "FRENAR"
    elif any(r.resultado != "OK" for r in revisiones):
        decision = "ESCALAR"
    else:
        decision = "PAGAR"

    nivel = nivel_de_revisiones(revisiones)
    if decision == "FRENAR":
        nivel = "NINGUNO"
    elif decision == "ESCALAR":
        nivel = nivel_max(nivel, "PERSONA")                              # alguien debe revisar
    elif nivel != "NINGUNO":                                             # R1.2
        decision = "ESCALAR"

    try:
        base, tasa = a_base(f.monto, f.moneda, ctx)
    except (NoEvaluable, ArithmeticError):                               # un monto absurdo (1E100) no rompe el motor
        base = tasa = None
    try:
        o = calendario.emparejar(f, ctx, reglas)
    except Exception:
        o = None
    try:
        canal = sugerir_canal(f, ctx, reglas) if decision != "FRENAR" else None   # R7.1
    except Exception:
        canal = None
    return Resultado(decision=decision, nivel=nivel, revisiones=revisiones,
                     motivo=_motivo(decision, nivel, revisiones, o and o.id),
                     version_reglas=reglas.version, tasa_usada=tasa, monto_base=base,
                     canal=canal, obligacion_id=o.id if o else None)
