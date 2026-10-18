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

Las marcas se calculan al cargar, no se escriben a mano. Al importar las órdenes, `proveedor_id` se toma del registro de proveedores buscando por nombre y comprobando la identificación tributaria; el `ID_Proveedor` del archivo de órdenes no se usa, porque el listado de 200 renumeró los ID (OCD12). `Contexto` gana `proveedores: dict[str, Proveedor]` (por nombre normalizado) y `ordenes: dict[str, OrdenCompra]` (por número), y `contexto_desde_acta` agrega `oc_facturadas: dict[str, str]` (número → factura).

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

## Migración de los beneficiarios de ejemplo (OCD4, OT2)

`cargar_contexto_base` arma `ctx.registros` desde `proveedores.yaml` (país como código ISO: Colombia → CO, México → MX, Perú → PE, Ecuador → EC; cuenta ficticia) y le suma el acuerdo de `registros.yaml`, que ahora solo tiene `acuerdos` e `historial`. La lógica de las revisiones no cambia: siguen leyendo `ctx.registros`.

Cada beneficiario de ejemplo pasó a un proveedor válido con el mismo papel en los casos:

| Antes | Ahora | País | Moneda | Acuerdo |
|---|---|---|---|---|
| Pixel Norte Ltda. | Tecnología Cafetera S.A.S. | CO | COP | 2.400.000 |
| Diseños Alba | Textiles Modernos Pereira S.A.S. | CO | COP | 4.100.000 |
| Imprenta Sol | Alimentos del Valle S.A.S. | CO | COP | 6.000.000 |
| Hosting Andes | Consultores Energéticos Magdalena S.A.S. | CO | COP | sin acuerdo |
| Contador externo | Laboratorios Clínicos Cundinamarca S.A.S. | CO | COP | 1.500.000 |
| Obras Cumbre SAS | Inversiones Metalmecánicos Cauca S.A.S. | CO | COP | 60.000.000 |
| Taller Azteca | Papelería Corporativa Anáhuac S.A. de C.V. | MX | MXN | 12.500 |
| Cloudwerk GmbH (Alemania) | Tecnología Quiteña S.A. | EC | USD | 540 |
| Estúdio Verde (Brasil) | Importadora Químicos Rímac S.A.C. | PE | PEN | 2.420 (antes 3.520 BRL) |

- **Brasil y Alemania no están en el listado de válidos.** Sus papeles pasan a Perú y Ecuador. En Ecuador la moneda sigue siendo USD, así que los montos no cambian. En Perú los montos se convirtieron de BRL a PEN con las tasas de ejemplo (750 y 1.090 COP): el acuerdo de 3.520 BRL pasa a 2.420 PEN y la factura de 3.800 BRL a 2.615 PEN, que sigue un 8 % sobre lo acordado (zona gris, escala a la persona).
- **Canal sugerido:** Perú en PEN usa «Transferencia bancaria (Perú)»; Ecuador en USD, SWIFT o USDC (ya no hay SEPA ni Pix en los ejemplos).
- **Cuentas:** las facturas de ejemplo traen la cuenta ficticia del proveedor (`Cuenta demo ···NNNN`), para que R4.2 las reconozca.
- **Lo que no cambia:** los proveedores ficticios fuera de la lista («Nuevo Proveedor SAS», «Estudio Nube SAS», «Otros SAS») siguen fuera, a propósito, para los casos de beneficiario nuevo.
- **Datos de salas ya creadas:** el acta es de solo añadir. Las salas que ya existían en la demo desplegada conservan sus decisiones con los nombres anteriores; las salas nuevas usan los proveedores válidos.
- **Pendiente:** las maquetas del PDF `docs/Ruta-de-una-factura.pdf` muestran los nombres anteriores y se regeneran a mano (P6).

## Ajustes al construir (versión mínima, 17 oct)

- **La lista permitida ya sale de `proveedores.yaml`** (migración de abajo, OC1.6). Sin OC ni acuerdo, la factura de un proveedor sigue escalando a `PERSONA` (R3.5).
- **Las marcas escalan aunque la factura no cite OC.** Un proveedor con «identificación repetida» o «inválida» va al senior siempre (OC4.4), no solo cuando hay OC: si no, citar o no una OC cambiaría la decisión. El listado de válidos no trae ninguno marcado; la regla queda para cuando entre otro listado y se prueba con un proveedor marcado a mano.
- **Revisión sin OC:** si la factura no cita OC, la revisión OC4 da `OK` y no cambia nada más (OC4.8, `oc_obligatoria` queda fuera de esta versión).
- **La OC hace las veces de acuerdo (OC4.1) solo en R3.5:** si el proveedor tiene acuerdo registrado, R3.2 sigue como siempre. **No reemplaza el calendario:** una factura con OC que no estaba en el calendario sigue dando `AVISO` de R6.2 y escala a `PERSONA`. Para pagar sola, la OC debe cuadrar **y** la obligación estar en el calendario (OC4.9).
- **Estado «facturada»:** `contexto_desde_acta` lo calcula con las facturas en estado `PAGADA` o `PENDIENTE` cuyo `ficha.orden_compra` coincide (OC5.2). No hay estado guardado aparte.
- **Datos:** `data/ordenes_compra.yaml` es **sintético**, usa proveedores del listado de **válidos** (por eso OCD13 no le afecta) y está marcado como tal. Se valida al cargar (OC2.2): número repetido, proveedor inexistente o cuentas que no cuadran lo rechazan. Si el archivo falla, el registro queda vacío y toda OC citada da «inexistente» (senior): falla seguro (OC1.5).
- **Fuera de esta versión:** lectura de la OC por el agente de entrada (OT5), página de órdenes (OT7), columna en `facturas.csv` y el importador del `.xlsx`.
