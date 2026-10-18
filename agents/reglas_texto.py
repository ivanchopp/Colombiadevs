"""Agente de reglas en lenguaje natural (spec agente-de-reglas, AR).

La IA (o el lector por patrones) solo PROPONE; este módulo nunca cambia una regla. Convierte una propuesta
cerrada en valores del formulario de la página de reglas, con Decimal y en código (AR2.2). Lo demás (vista
previa, firma, techo duro, motivo, acta) lo hace el formulario de siempre (AR1.2, AR1.3)."""
import re
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .segunda_lectura import parsear_monto

LARGO_MAX = 500
CAMBIOS_MAX = 4
OPERACIONES = ("fijar", "subir_monto", "bajar_monto", "subir_porcentaje", "bajar_porcentaje")
ESTADOS = ("propuesta", "aclaracion", "no_entendido", "fuera_de_alcance")
EJEMPLO = "Por ejemplo: «fija el pago automático en 1.000 dólares» o «sube el presupuesto un 20 %»."

# parámetro -> (tipo, cómo se nombra, patrón del vocabulario fijo)
PARAMETROS = {
    "limite_periodo_beneficiario": ("monto", "el límite por proveedor y periodo",
                                    r"l[ií]mite (?:mensual |del periodo )?(?:por|del|de cada) (?:proveedor|beneficiario)|"
                                    r"tope (?:mensual )?por (?:proveedor|beneficiario)"),
    "persona_max": ("monto", "lo que aprueba la persona de finanzas",
                    r"l[ií]mite de (?:la )?persona|aprobaci[oó]n de (?:la )?persona|m[aá]ximo (?:de |para )?(?:la )?persona|"
                    r"persona de finanzas"),
    "autopago_max": ("monto", "el pago automático", r"pago autom[aá]tico|autopago|pago sin (?:aprobaci[oó]n|revisi[oó]n)"),
    "presupuesto_periodo": ("monto", "el presupuesto del periodo", r"presupuesto"),
    "tolerancia_frenar": ("porcentaje", "la tolerancia para frenar",
                          r"tolerancia (?:para|de|al) (?:frenar|freno)|tolerancia m[aá]xima"),
    "tolerancia_ok": ("porcentaje", "la tolerancia normal", r"tolerancia (?:normal|ok|aceptada)"),
    "ventana_dias": ("dias", "el margen de días del calendario",
                     r"ventana(?: del calendario)?|margen de d[ií]as|d[ií]as de margen"),
}
VERBOS = {
    "fijar": r"fij(?:a|ar|e)|pon(?:er|ga)?|establec(?:e|er)|cambia(?:r)?|deja(?:r)?|ajusta(?:r)?|configura(?:r)?",
    "subir": r"sub(?:e|ir)|aument(?:a|ar)|increment(?:a|ar)|elev(?:a|ar)",
    "bajar": r"baj(?:a|ar)|reduc(?:e|ir)|disminuy(?:e|ir)|recort(?:a|ar)",
}
FUERA_DE_ALCANCE = [
    (r"techo", "El techo duro no se cambia por texto: lo fija ingeniería (R9.5)."),
    (r"a partir de|desde (?:el |ma[nñ]ana|hoy)|vigencia|el pr[oó]ximo (?:lunes|mes)|la pr[oó]xima semana",
     "Los cambios rigen desde que se confirman; las fechas de vigencia no se piden por texto (PP8.7)."),
    (r"proveedores? nuevos?|lista de proveedores|agrega(?:r)? (?:un )?proveedor|elimina(?:r)? (?:al |un )?proveedor",
     "La lista de proveedores no se cambia desde las reglas."),
]
MULTIPLICADORES = {"mil": Decimal(1000), "k": Decimal(1000), "millon": Decimal(10) ** 6, "millones": Decimal(10) ** 6}
RE_NUMERO = re.compile(r"(?<![\w.,])(?P<n>\d[\d.,]*)(?P<pct>\s*(?:%|por ciento))?"
                       r"(?:\s*(?P<mult>mil|millones|mill[oó]n|k)\b)?")
MONEDAS = [(r"pesos? mexicanos?|mxn", "MXN"), (r"d[oó]lares?|usd|us\$", "USD"), (r"euros?|eur", "EUR"),
           (r"pesos?|cop", "COP")]


class ErrorPedido(Exception):
    """El pedido no se puede convertir en un cambio. El mensaje se muestra a la persona."""


class CambioPedido(BaseModel):
    model_config = ConfigDict(extra="forbid")
    parametro: Literal["autopago_max", "persona_max", "limite_periodo_beneficiario", "presupuesto_periodo",
                       "tolerancia_ok", "tolerancia_frenar", "ventana_dias"]
    operacion: Literal["fijar", "subir_monto", "bajar_monto", "subir_porcentaje", "bajar_porcentaje"]
    valor: Decimal = Field(ge=0)
    moneda: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")


class Propuesta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: Literal["propuesta", "aclaracion", "no_entendido", "fuera_de_alcance"]
    cambios: list[CambioPedido] = Field(default_factory=list, max_length=CAMBIOS_MAX)
    pregunta: str | None = Field(default=None, max_length=300)


@dataclass
class Resolucion:
    valores: dict = field(default_factory=dict)        # clave -> entero en las unidades del formulario
    avisos: list = field(default_factory=list)


@dataclass
class Resultado:
    estado: str
    lector: str
    pedido: str
    pregunta: str | None = None
    cambios: list = field(default_factory=list)
    valores: dict = field(default_factory=dict)
    avisos: list = field(default_factory=list)
    senales: list = field(default_factory=list)

    @property
    def dudosa(self) -> bool:
        return bool(self.senales)


# ---------------------------------------------------------------- números y vocabulario (código, no lenguaje)
def numeros(texto: str) -> list[tuple[Decimal, bool, int, int]]:
    """(valor, es_porcentaje, inicio, fin) de cada número del texto. «1.000», «1,5 millones», «20 %»."""
    salida = []
    for m in RE_NUMERO.finditer(texto.lower()):
        base = m.group("n").rstrip(".,")
        valor = parsear_monto(base)
        if valor is None:
            continue
        if m.group("mult"):
            valor *= MULTIPLICADORES[m.group("mult").replace("ó", "o")]
        salida.append((valor, bool(m.group("pct")), m.start(), m.end()))
    return salida


def menciones(texto: str) -> list[tuple[str, int, int]]:
    """(parámetro, inicio, fin) de cada mención del vocabulario fijo, sin solaparse."""
    usados, salida = [], []
    for clave, (_t, _n, patron) in PARAMETROS.items():
        for m in re.finditer(patron, texto.lower()):
            if not any(m.start() < f and i < m.end() for i, f in usados):
                usados.append((m.start(), m.end()))
                salida.append((clave, m.start(), m.end()))
    return sorted(salida, key=lambda x: x[1])


# ---------------------------------------------------------------- lector por patrones (AR6)
def _moneda_cerca(texto: str, fin: int) -> str | None:
    cola = texto[fin:fin + 28]
    for patron, codigo in MONEDAS:
        if re.match(rf"\s*(?:de\s+)?(?:{patron})\b", cola):
            return codigo
    return None


def _clausulas(t: str) -> list[str]:
    cortes = [m.start() for m in re.finditer(rf"(?:;|,|\by\b)\s*(?=(?:{'|'.join(VERBOS.values())})\b)", t)]
    partes, ini = [], 0
    for c in cortes:
        partes.append(t[ini:c])
        ini = c
    partes.append(t[ini:])
    return [re.sub(r"^[;,\s]*(?:y\s+)?", "", p).strip() for p in partes if p.strip(" ;,")]


def _leer_clausula(c: str) -> CambioPedido:
    ment = menciones(c)
    if not ment:
        raise ErrorPedido("No encuentro de qué regla hablas.")
    if len(ment) > 1:
        raise ErrorPedido("Menciona dos reglas a la vez; pídelas por separado.")
    clave, _, fin = ment[0]
    tipo = PARAMETROS[clave][0]
    verbo = next((v for v, p in VERBOS.items() if re.search(rf"\b(?:{p})\b", c)), None)
    if verbo is None:
        raise ErrorPedido("No encuentro qué quieres hacer (fijar, subir o bajar).")
    nums = [n for n in numeros(c) if n[2] >= fin]
    if not nums:
        raise ErrorPedido("No encuentro el valor.")
    valor, es_pct, ini_n, fin_n = nums[0]
    puente = c[fin:ini_n].strip()
    absoluto = verbo == "fijar" or bool(re.search(r"\b(?:a|hasta|al)\s*(?:un\s+|el\s+)?$", puente + " "))
    if tipo == "monto" and es_pct and absoluto:
        raise ErrorPedido("Un monto no se fija en porcentaje.")
    if absoluto:
        op = "fijar"
    elif es_pct:
        op = "subir_porcentaje" if verbo == "subir" else "bajar_porcentaje"
    else:
        op = "subir_monto" if verbo == "subir" else "bajar_monto"
    moneda = _moneda_cerca(c, fin_n) if tipo == "monto" and not es_pct else None
    return CambioPedido(parametro=clave, operacion=op, valor=valor, moneda=moneda)


def leer_con_patrones(pedido: str) -> Propuesta:
    """Solo frases simples; todo lo demás es «no entendido» y no se adivina (AR2.7, AR6.2)."""
    t = pedido.lower()
    for patron, razon in FUERA_DE_ALCANCE:
        if re.search(patron, t):
            return Propuesta(estado="fuera_de_alcance", pregunta=razon)
    cambios = []
    try:
        clausulas = _clausulas(t)
        if len(clausulas) > CAMBIOS_MAX:
            raise ErrorPedido(f"Pides más de {CAMBIOS_MAX} cambios a la vez.")
        cambios = [_leer_clausula(c) for c in clausulas]
    except (ErrorPedido, ValidationError) as e:
        motivo = e.args[0] if isinstance(e, ErrorPedido) else "El valor no es válido."
        return Propuesta(estado="no_entendido", pregunta=f"{motivo} {EJEMPLO}")
    if not cambios:
        return Propuesta(estado="no_entendido", pregunta=f"No entendí el pedido. {EJEMPLO}")
    return Propuesta(estado="propuesta", cambios=cambios)


# ---------------------------------------------------------------- resolución con Decimal (AR2.2, AR2.3)
def resolver(propuesta: Propuesta, actuales, tasas: dict) -> Resolucion:
    """Valores del formulario (enteros) a partir del valor vigente. Lanza ErrorPedido si no se puede."""
    res, vistos = Resolucion(), set()
    for c in propuesta.cambios:
        if c.parametro in vistos:
            raise ErrorPedido(f"Pides {PARAMETROS[c.parametro][1]} dos veces; deja un solo cambio por regla.")
        vistos.add(c.parametro)
        tipo, nombre, _ = PARAMETROS[c.parametro]
        actual = Decimal(str(getattr(actuales, c.parametro)))
        base = actual * 100 if tipo == "porcentaje" else actual
        v = c.valor
        if tipo == "monto" and c.operacion in ("fijar", "subir_monto", "bajar_monto") and c.moneda \
                and c.moneda != actuales.moneda_base:
            tasa = tasas.get(c.moneda)
            if tasa is None:
                raise ErrorPedido(f"No tengo tipo de cambio para {c.moneda}: dime el monto en {actuales.moneda_base}.")
            v = v * Decimal(str(tasa))
            res.avisos.append(f"{c.valor} {c.moneda} se convirtió a {actuales.moneda_base} con la tabla de cambio (supuesto).")
        nuevo = {"fijar": v, "subir_monto": base + v, "bajar_monto": base - v,
                 "subir_porcentaje": base * (1 + v / 100), "bajar_porcentaje": base * (1 - v / 100)}[c.operacion]
        entero = nuevo.quantize(Decimal(1), ROUND_HALF_UP)
        if entero != nuevo:
            res.avisos.append(f"{nombre.capitalize()}: el valor {nuevo.normalize():f} se redondeó a {entero}.")
        if entero < 0:
            raise ErrorPedido(f"{nombre.capitalize()} quedaría negativo.")
        if tipo == "porcentaje" and entero > 100:
            raise ErrorPedido(f"{nombre.capitalize()} no puede pasar de 100 %.")
        res.valores[c.parametro] = int(entero)
    return res


# ---------------------------------------------------------------- comprobación de coherencia (AR2.8)
def comprobar_coherencia(pedido: str, propuesta: Propuesta) -> list[str]:
    """Compara la propuesta con el texto SIN interpretar el lenguaje. Devuelve las señales de duda."""
    senales = []
    n_menciones = len(menciones(pedido))
    if n_menciones > len(propuesta.cambios):
        senales.append(f"El pedido nombra {n_menciones} regla(s) y la propuesta trae {len(propuesta.cambios)} cambio(s).")
    del_texto = [n[0] for n in numeros(pedido)]
    valores = [c.valor for c in propuesta.cambios]
    for n in del_texto:
        if n not in valores:
            senales.append(f"El número {n.normalize():f} del pedido no aparece en ningún cambio.")
    relativos = re.search(r"\b(?:doble|triple|mitad)\b", pedido.lower())
    for v in valores:
        if v not in del_texto and not relativos:
            senales.append(f"El valor {v.normalize():f} de la propuesta no está en el pedido.")
    return senales


# ---------------------------------------------------------------- entrada para la página
def entender(pedido: str, actuales, tasas: dict, cliente=None) -> Resultado:
    """Pedido de texto -> Resultado. Nunca escribe nada: lo aplica la persona desde el formulario."""
    pedido = (pedido or "").strip()
    if not 1 <= len(pedido) <= LARGO_MAX:
        return Resultado("no_entendido", "patrones", pedido[:LARGO_MAX],
                         pregunta=f"Escribe entre 1 y {LARGO_MAX} caracteres. {EJEMPLO}")
    propuesta, lector = leer_con_patrones(pedido), "patrones"
    r = Resultado(propuesta.estado, lector, pedido, pregunta=propuesta.pregunta, cambios=propuesta.cambios)
    if propuesta.estado != "propuesta":
        return r
    try:
        res = resolver(propuesta, actuales, tasas)
    except ErrorPedido as e:
        return Resultado("no_entendido", lector, pedido, pregunta=str(e))
    r.valores, r.avisos = res.valores, res.avisos
    r.senales = comprobar_coherencia(pedido, propuesta)
    return r
