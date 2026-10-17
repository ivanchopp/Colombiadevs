"""Proyección: estado de cada factura a partir del acta (AC4)."""
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class Factura:
    factura_id: str
    estado: str
    decision: dict                      # payload del evento DECISION
    fila_decision: int
    creado_en: str
    resuelto_en: str | None = None
    respuesta: dict | None = None       # payload de APROBACION o RECHAZO
    aprobador: str | None = None
    fila_acta: int = 0
    huella: str = ""
    intentos: list = field(default_factory=list)

    @property
    def monto_base(self) -> Decimal:
        return Decimal(self.decision["monto_base"])


def facturas_por_estado(filas) -> dict[str, Factura]:
    res: dict[str, Factura] = {}
    for f in filas:
        if f.factura_id is None:
            continue
        if f.tipo == "DECISION":
            d = f.payload["decision"]
            estado = "PAGADA" if d == "PAGAR" else "FRENADA" if d == "FRENAR" else "PENDIENTE"
            res[f.factura_id] = Factura(f.factura_id, estado, f.payload, f.num, f.creado_en,
                                        f.creado_en if estado != "PENDIENTE" else None,
                                        fila_acta=f.num, huella=f.huella)
        elif f.factura_id in res:
            r = res[f.factura_id]
            if f.tipo in ("APROBACION", "RECHAZO") and r.estado == "PENDIENTE":
                r.estado = "PAGADA" if f.tipo == "APROBACION" else "RECHAZADA"
                r.respuesta, r.aprobador, r.resuelto_en = f.payload, f.actor, f.creado_en
                r.fila_acta, r.huella = f.num, f.huella
            elif f.tipo == "INTENTO_RECHAZADO":
                r.intentos.append(f.payload)
    return res


ESTADO_PUBLICO = {"PAGADA": "resuelta", "FRENADA": "resuelta", "RECHAZADA": "resuelta",
                  "PENDIENTE": "en revisión"}


def estado_publico(factura: Factura) -> str:
    """Lista cerrada de salidas: nunca motivos, reglas ni montos (AC4.3)."""
    return ESTADO_PUBLICO.get(factura.estado, "en revisión")
