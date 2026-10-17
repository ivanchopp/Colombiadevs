# Diseño: órdenes de compra y proveedores

Estado: **borrador para revisión del equipo**. Requisitos: `requirements.md`.
Sigue el diseño del motor (`specs/motor-de-reglas/design.md`): función pura, fallo seguro y todas las revisiones corren.

## Archivos

```
data/
├─ proveedores.yaml                          # generado: id, nombre, pais, id_tributaria, tipo_id, cuenta (OC1)
├─ ordenes_compra.yaml                       # generado: sin la columna Simulacion_Discrepancia (OC2.4)
└─ importar_compras.py                       # convierte los .xlsx a YAML y valida (OC1, OC2)
engine/
├─ compras.py                                # cargar y validar proveedores y OC; estado de cada OC desde el acta
└─ revisiones/orden_compra.py                # la revisión OC4
app/pages/6_Ordenes_de_compra.py             # OC6.1
```

Los YAML se generan una vez con `python data/importar_compras.py <ruta a los .xlsx>` y se suben al repositorio, para que la aplicación no dependa de leer Excel en Railway (y no sume `openpyxl` a producción). **Los .xlsx originales no se suben:** el repositorio es público y traen dirección, teléfono y correo de cada proveedor. Solo pasan al YAML los campos de OC1.1 y OC2.1.

## Modelos

```python
class Proveedor(Cerrado):
    id: int
    nombre: str
    pais: str
    id_tributaria: str
    tipo_id: Literal["NIT", "RFC", "RUC"]
    cuenta: str                         # ficticia, OCD3
    marcas: list[Literal["identificacion_repetida", "identificacion_invalida"]] = []

class OrdenCompra(Cerrado):
    numero: str                         # "PO-2026-001"
    proveedor_id: int
    id_tributaria: str
    articulo: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    moneda: str = "COP"                 # OCD1
    marcas: list[Literal["no_coincide_con_proveedor"]] = []
```

Las marcas se calculan al cargar, no se escriben a mano. `Contexto` gana `proveedores: dict[str, Proveedor]` (por nombre normalizado) y `ordenes: dict[str, OrdenCompra]` (por número), y `contexto_desde_acta` agrega `oc_facturadas: dict[str, str]` (número → factura).

`Ficha` gana `orden_compra: str | None = None` e `id_tributaria: str | None = None`; `origen_campos` admite la clave `orden_compra`.

## La revisión (OC4)

```python
def revisar(ficha, ctx, reglas):
    if not ficha.orden_compra:
        return [aviso_sin_oc] if reglas.oc_obligatoria else [ok("sin OC: sigue acuerdo y calendario")]
    oc = ctx.ordenes.get(normalizar_oc(ficha.orden_compra))
    if oc is None:                                   return [senior("orden de compra inexistente")]          # OC4.2
    prov = ctx.proveedores_por_id.get(oc.proveedor_id)
    if (prov is None or prov.nombre != ficha.beneficiario
            or ficha.id_tributaria not in (None, oc.id_tributaria)
            or oc.id_tributaria != prov.id_tributaria): return [senior("identificación tributaria no coincide")] # OC4.3
    if prov.marcas or oc.marcas:                     return [senior("identificación repetida o inválida")]     # OC4.4
    if oc.numero in ctx.oc_facturadas and ctx.oc_facturadas[oc.numero] != ficha.factura_id:
        return [frenar("orden de compra ya facturada")]                                                       # OC4.6
    exceso = (a_base(ficha.monto, ficha.moneda) - a_base(oc.total, oc.moneda)) / a_base(oc.total, oc.moneda)  # OC4.7
    return [tolerancias(exceso, reglas)]                                                                       # OC4.1, OC4.5
```

- **Orden:** va después de beneficiario (R4) y antes de acuerdo (R3.2). Cuando la OC da `OK`, `frenar.acuerdo` no emite «sin acuerdo registrado» para esa factura (OC4.1); el resto sigue igual (OC4.9).
- **`id_tributaria` vacía en la factura:** no basta para pagar con OC. Si falta, la revisión da `AVISO` y escala a `PERSONA`, porque el emisor no se pudo confirmar.
- **Normalizar el número:** mayúsculas, sin espacios; `po 2026 001`, `PO-2026-001` y `PO2026001` son la misma OC.

## Estado de la OC (OC5)

`contexto_desde_acta` ya recorre las decisiones para el calendario. Se suma: si el payload de `DECISION` trae `orden_compra` y la factura está `PAGADA` o `PENDIENTE`, esa OC queda facturada por esa factura. `FRENADA` y `RECHAZADA` la dejan abierta.

## Pruebas

- `tests/test_ordenes_compra.py`: una prueba por criterio (OC1 a OC5), con los YAML generados.
- `casos.yaml`: los 8 casos de OC7.1. `eval.py` los suma al conteo.
- Hypothesis: estrategia nueva que genera fichas con OC inexistente, ajena, facturada o con monto alterado (OC8.2).

## Riesgos

| Riesgo | Mitigación |
|---|---|
| La moneda de las OC se interpreta mal (OCD1) | Se marca «supuesto» en pantalla y en el CSV; un cambio de moneda es un dato, no código |
| Una OC válida hace pasar un pago que otra regla frenaría | OC4.9: la OC solo reemplaza la falta de acuerdo; el resto de revisiones corre igual y el guardarraíl revalida |
| El proveedor inventa un número de OC por chat | OC4.10 y OC3.3: el agente no sabe qué OC existen y un dato solo aclarado escala |
| El archivo trae errores de datos (IDs repetidos) | Se marcan al cargar y escalan al senior; no se corrigen en silencio |
